/**
 * Annotation Tools
 * 
 * Toolbar with annotation tools and color picker
 */

import React from 'react';
import {
  HighlighterIcon,
  MessageSquareIcon,
  SquareIcon,
  MousePointerIcon,
} from 'lucide-react';
import { AnnotationType, AnnotationColor, AnnotationToolsProps } from './types';

const TOOLS = [
  {
    type: null,
    label: 'Seleccionar',
    icon: MousePointerIcon,
    description: 'Modo selección (click en anotaciones)',
  },
  {
    type: AnnotationType.HIGHLIGHT,
    label: 'Resaltar',
    icon: HighlighterIcon,
    description: 'Resaltar texto (arrastra para dibujar)',
  },
  {
    type: AnnotationType.STICKY_NOTE,
    label: 'Nota',
    icon: MessageSquareIcon,
    description: 'Agregar nota adhesiva (click para ubicar)',
  },
  {
    type: AnnotationType.REDACTION,
    label: 'Redactar',
    icon: SquareIcon,
    description: 'Redactar información sensible (negro sólido)',
  },
];

const COLORS = [
  { name: 'Amarillo', value: AnnotationColor.YELLOW },
  { name: 'Verde', value: AnnotationColor.GREEN },
  { name: 'Azul', value: AnnotationColor.BLUE },
  { name: 'Rojo', value: AnnotationColor.RED },
  { name: 'Morado', value: AnnotationColor.PURPLE },
  { name: 'Naranja', value: AnnotationColor.ORANGE },
];

export const AnnotationTools: React.FC<AnnotationToolsProps> = ({
  selectedTool,
  selectedColor,
  onToolSelect,
  onColorSelect,
  disabled = false,
}) => {
  return (
    <div className="bg-white border border-gray-300 rounded-lg shadow-md p-3">
      {/* Title */}
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-gray-700">
          Herramientas de Anotación
        </h3>
        <p className="text-xs text-gray-500 mt-1">
          {selectedTool === null && 'Modo selección activo'}
          {selectedTool === AnnotationType.HIGHLIGHT && 'Arrastra para resaltar'}
          {selectedTool === AnnotationType.STICKY_NOTE && 'Click para agregar nota'}
          {selectedTool === AnnotationType.REDACTION && 'Arrastra para redactar'}
        </p>
      </div>

      {/* Tools */}
      <div className="space-y-2 mb-4">
        {TOOLS.map((tool) => {
          const Icon = tool.icon;
          const isSelected = selectedTool === tool.type;
          
          return (
            <button
              key={tool.label}
              onClick={() => onToolSelect(tool.type)}
              disabled={disabled}
              className={`
                w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors
                ${isSelected
                  ? 'bg-blue-100 border-2 border-blue-500 text-blue-700'
                  : 'bg-gray-50 border-2 border-transparent text-gray-700 hover:bg-gray-100'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
              title={tool.description}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <div className="flex-1 text-left">
                <div className="text-sm font-medium">{tool.label}</div>
                <div className="text-xs text-gray-500">{tool.description}</div>
              </div>
              {isSelected && (
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
              )}
            </button>
          );
        })}
      </div>

      {/* Color Picker */}
      {selectedTool !== null && selectedTool !== AnnotationType.REDACTION && (
        <div className="pt-3 border-t border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Color
          </label>
          <div className="grid grid-cols-3 gap-2">
            {COLORS.map((color) => (
              <button
                key={color.value}
                onClick={() => onColorSelect(color.value)}
                disabled={disabled}
                className={`
                  relative w-full h-10 rounded-lg border-2 transition-all
                  ${selectedColor === color.value
                    ? 'border-gray-800 scale-105'
                    : 'border-gray-300 hover:border-gray-400'
                  }
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                `}
                style={{ backgroundColor: color.value }}
                title={color.name}
              >
                {selectedColor === color.value && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-4 h-4 bg-white rounded-full border-2 border-gray-800" />
                  </div>
                )}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Color seleccionado: {COLORS.find(c => c.value === selectedColor)?.name}
          </p>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <h4 className="text-xs font-semibold text-gray-700 mb-1">
          Atajos de teclado
        </h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">Esc</kbd> - Modo selección</li>
          <li>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">H</kbd> - Resaltar</li>
          <li>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">N</kbd> - Nota adhesiva</li>
          <li>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">R</kbd> - Redactar</li>
          <li>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">Del</kbd> - Eliminar selección</li>
        </ul>
      </div>

      {/* Stats */}
      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600 text-center">
          {disabled ? (
            <span className="text-amber-600">⚠️ Cargando documento...</span>
          ) : (
            <span className="text-green-600">✓ Anotaciones activas</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnnotationTools;
