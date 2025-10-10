"""
Sistema de notificaciones para alertas de validación.

Soporta:
- Email (SMTP)
- Slack (Webhook)
- Templates HTML personalizables
- Prioridades (LOW, MEDIUM, HIGH, CRITICAL)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import aiohttp
import os
from jinja2 import Template

logger = logging.getLogger(__name__)


class AlertPriority(str, Enum):
    """Niveles de prioridad de alertas."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NotificationService:
    """Servicio central de notificaciones."""

    def __init__(self):
        """Inicializa el servicio de notificaciones."""
        # Email config
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        
        # Slack config
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        
        # Alert recipients
        self.default_recipients = os.getenv(
            "ALERT_RECIPIENTS",
            "compliance@company.com,security@company.com"
        ).split(",")
        
        self._session = None

    async def __aenter__(self):
        """Context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            await self._session.close()

    async def send_sanctions_alert(
        self,
        entity_name: str,
        entity_type: str,
        matches: List[Dict],
        confidence: float,
        document_id: Optional[int] = None,
        priority: AlertPriority = AlertPriority.HIGH,
        recipients: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """
        Envía alerta de entidad sancionada.

        Args:
            entity_name: Nombre de la entidad
            entity_type: Tipo (PERSON, COMPANY, etc.)
            matches: Lista de matches encontrados
            confidence: Nivel de confianza (0-1)
            document_id: ID del documento (opcional)
            priority: Prioridad de la alerta
            recipients: Lista de destinatarios (usa default si None)

        Returns:
            Dict con resultado de envíos {"email": bool, "slack": bool}
        """
        results = {}
        
        # Preparar datos de alerta
        alert_data = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "matches": matches,
            "confidence": confidence,
            "confidence_pct": f"{confidence * 100:.1f}%",
            "document_id": document_id,
            "priority": priority.value,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": [m["source"] for m in matches],
        }

        # Enviar email
        if self.smtp_user and self.smtp_password:
            try:
                email_sent = await self._send_email_alert(
                    alert_data,
                    recipients or self.default_recipients
                )
                results["email"] = email_sent
                logger.info(f"Email alert sent for entity: {entity_name}")
            except Exception as e:
                logger.error(f"Error sending email alert: {e}")
                results["email"] = False
        
        # Enviar Slack
        if self.slack_webhook_url:
            try:
                slack_sent = await self._send_slack_alert(alert_data)
                results["slack"] = slack_sent
                logger.info(f"Slack alert sent for entity: {entity_name}")
            except Exception as e:
                logger.error(f"Error sending Slack alert: {e}")
                results["slack"] = False

        return results

    async def _send_email_alert(
        self,
        alert_data: Dict,
        recipients: List[str]
    ) -> bool:
        """
        Envía alerta por email con template HTML.
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._get_email_subject(alert_data)
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)

            # Template HTML
            html_content = self._render_email_template(alert_data)
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, recipients, msg.as_string())

            return True

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False

    async def _send_slack_alert(self, alert_data: Dict) -> bool:
        """
        Envía alerta a Slack usando webhook.
        """
        try:
            # Formato Slack
            color = self._get_slack_color(alert_data["priority"])
            
            slack_message = {
                "text": f"🚨 *Alerta de Validación de Sanciones*",
                "attachments": [
                    {
                        "color": color,
                        "title": f"Entidad Sancionada Detectada: {alert_data['entity_name']}",
                        "fields": [
                            {
                                "title": "Tipo de Entidad",
                                "value": alert_data["entity_type"],
                                "short": True
                            },
                            {
                                "title": "Confianza",
                                "value": alert_data["confidence_pct"],
                                "short": True
                            },
                            {
                                "title": "Fuentes",
                                "value": ", ".join(alert_data["sources"]),
                                "short": False
                            },
                            {
                                "title": "Matches Encontrados",
                                "value": f"{len(alert_data['matches'])} coincidencias",
                                "short": True
                            },
                            {
                                "title": "Prioridad",
                                "value": alert_data["priority"],
                                "short": True
                            },
                        ],
                        "footer": "Sistema FinancIA 2030 - Validación de Terceros",
                        "ts": int(datetime.utcnow().timestamp())
                    }
                ]
            }

            if alert_data.get("document_id"):
                slack_message["attachments"][0]["fields"].append({
                    "title": "Documento",
                    "value": f"<http://localhost:3000/documents/{alert_data['document_id']}|Ver Documento #{alert_data['document_id']}>",
                    "short": False
                })

            # Enviar a Slack
            async with self._session.post(
                self.slack_webhook_url,
                json=slack_message,
                timeout=10
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Slack send error: {e}")
            return False

    def _get_email_subject(self, alert_data: Dict) -> str:
        """Genera subject del email según prioridad."""
        priority = alert_data["priority"]
        entity = alert_data["entity_name"]
        
        if priority == AlertPriority.CRITICAL.value:
            return f"🚨 CRÍTICO: Entidad Sancionada - {entity}"
        elif priority == AlertPriority.HIGH.value:
            return f"⚠️ ALTA: Entidad Sancionada - {entity}"
        elif priority == AlertPriority.MEDIUM.value:
            return f"⚡ MEDIA: Posible Entidad Sancionada - {entity}"
        else:
            return f"ℹ️ INFO: Validación de Sanciones - {entity}"

    def _render_email_template(self, alert_data: Dict) -> str:
        """Renderiza template HTML del email."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .header {
            background-color: {{ header_color }};
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }
        .alert-box {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }
        .critical-box {
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .info-table td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .info-table td:first-child {
            font-weight: bold;
            width: 40%;
        }
        .match-item {
            background-color: #f0f0f0;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #007bff;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Alerta de Validación de Sanciones</h1>
        </div>
        <div class="content">
            <div class="alert-box {% if priority == 'CRITICAL' %}critical-box{% endif %}">
                <h2>⚠️ Entidad Sancionada Detectada</h2>
                <p><strong>{{ entity_name }}</strong> ha sido encontrada en listas de sanciones internacionales.</p>
            </div>

            <table class="info-table">
                <tr>
                    <td>Entidad:</td>
                    <td><strong>{{ entity_name }}</strong></td>
                </tr>
                <tr>
                    <td>Tipo:</td>
                    <td>{{ entity_type }}</td>
                </tr>
                <tr>
                    <td>Nivel de Confianza:</td>
                    <td><strong>{{ confidence_pct }}</strong></td>
                </tr>
                <tr>
                    <td>Prioridad:</td>
                    <td><span style="color: {{ priority_color }};">{{ priority }}</span></td>
                </tr>
                <tr>
                    <td>Fuentes:</td>
                    <td>{{ sources | join(', ') }}</td>
                </tr>
                {% if document_id %}
                <tr>
                    <td>Documento:</td>
                    <td>#{{ document_id }}</td>
                </tr>
                {% endif %}
                <tr>
                    <td>Fecha/Hora:</td>
                    <td>{{ timestamp }}</td>
                </tr>
            </table>

            <h3>Coincidencias Encontradas ({{ matches | length }}):</h3>
            {% for match in matches %}
            <div class="match-item">
                <strong>{{ match.source }}</strong>: {{ match.name }}<br>
                <small>Similitud: {{ match.similarity }}%</small>
                {% if match.program %}
                <br><small>Programa: {{ match.program | join(', ') }}</small>
                {% endif %}
            </div>
            {% endfor %}

            <div style="margin-top: 30px; padding: 15px; background-color: #d1ecf1; border-left: 4px solid #0c5460;">
                <strong>⚡ Acción Requerida:</strong><br>
                Esta entidad requiere revisión manual inmediata. No proceder con transacciones hasta completar la verificación.
            </div>

            {% if document_id %}
            <div style="text-align: center; margin-top: 20px;">
                <a href="http://localhost:3000/documents/{{ document_id }}" class="button">
                    Ver Documento Completo
                </a>
            </div>
            {% endif %}
        </div>
        <div class="footer">
            <p>Sistema FinancIA 2030 - Validación de Terceros</p>
            <p>Esta es una alerta automática. No responder a este email.</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)
        
        # Determinar colores según prioridad
        priority = alert_data["priority"]
        if priority == "CRITICAL":
            header_color = "#dc3545"
            priority_color = "#dc3545"
        elif priority == "HIGH":
            header_color = "#fd7e14"
            priority_color = "#fd7e14"
        elif priority == "MEDIUM":
            header_color = "#ffc107"
            priority_color = "#ffc107"
        else:
            header_color = "#17a2b8"
            priority_color = "#17a2b8"

        return template.render(
            **alert_data,
            header_color=header_color,
            priority_color=priority_color
        )

    def _get_slack_color(self, priority: str) -> str:
        """Retorna color para mensaje Slack según prioridad."""
        colors = {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#17a2b8",
        }
        return colors.get(priority, "#17a2b8")

    async def send_daily_summary(
        self,
        stats: Dict,
        period: str = "24h",
        recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Envía resumen diario de validaciones.

        Args:
            stats: Estadísticas del período
            period: Período del resumen
            recipients: Destinatarios

        Returns:
            True si se envió correctamente
        """
        try:
            summary_data = {
                "period": period,
                "total_validations": stats.get("total_validations", 0),
                "entities_flagged": stats.get("entities_flagged", 0),
                "flagged_percentage": stats.get("flagged_percentage", 0),
                "documents_processed": stats.get("documents_processed", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Email
            if self.smtp_user and self.smtp_password:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"📊 Resumen Diario de Validaciones - {period}"
                msg["From"] = self.from_email
                msg["To"] = ", ".join(recipients or self.default_recipients)

                html_content = self._render_summary_template(summary_data)
                html_part = MIMEText(html_content, "html")
                msg.attach(html_part)

                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(
                        self.from_email,
                        recipients or self.default_recipients,
                        msg.as_string()
                    )

                logger.info(f"Daily summary sent for period: {period}")
                return True

        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False

    def _render_summary_template(self, summary_data: Dict) -> str:
        """Renderiza template del resumen diario."""
        # Simplificado - implementar template completo
        return f"""
        <html>
        <body>
            <h2>📊 Resumen de Validaciones - {summary_data['period']}</h2>
            <p><strong>Total Validaciones:</strong> {summary_data['total_validations']}</p>
            <p><strong>Entidades Flagged:</strong> {summary_data['entities_flagged']}</p>
            <p><strong>Porcentaje:</strong> {summary_data['flagged_percentage']:.2f}%</p>
            <p><strong>Documentos Procesados:</strong> {summary_data['documents_processed']}</p>
        </body>
        </html>
        """
