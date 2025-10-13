/**
 * Annotation Layer
 * 
 * Canvas overlay for drawing and displaying annotations on PDF pages
 * Supports: Highlights, Sticky Notes, Redactions
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { MessageSquareIcon, XIcon } from 'lucide-react';
import {
  Annotation,
  AnnotationType,
  Position,
  AnnotationLayerProps,
} from './types';

export const AnnotationLayer: React.FC<AnnotationLayerProps> = ({
  documentId,
  pageNumber,
  pageWidth,
  pageHeight,
  scale,
  annotations,
  selectedTool,
  selectedColor,
  onAnnotationCreate,
  onAnnotationUpdate,
  onAnnotationDelete,
  onAnnotationSelect,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);
  const [currentRect, setCurrentRect] = useState<Position | null>(null);
  const [selectedAnnotation, setSelectedAnnotation] = useState<string | null>(null);
  const [hoveredAnnotation, setHoveredAnnotation] = useState<string | null>(null);
  const [showNoteDialog, setShowNoteDialog] = useState(false);
  const [noteContent, setNoteContent] = useState('');
  const [notePosition, setNotePosition] = useState<Position | null>(null);

  // Filter annotations for current page
  const pageAnnotations = annotations.filter(a => a.pageNumber === pageNumber);

  /**
   * Draw all annotations on canvas
   */
  const drawAnnotations = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw each annotation
    pageAnnotations.forEach(annotation => {
      const { position, color, type, id } = annotation;
      const isHovered = hoveredAnnotation === id;
      const isSelected = selectedAnnotation === id;

      ctx.save();

      // Scale position
      const x = position.x * scale;
      const y = position.y * scale;
      const width = position.width * scale;
      const height = position.height * scale;

      switch (type) {
        case AnnotationType.HIGHLIGHT:
          // Semi-transparent highlight
          ctx.fillStyle = color;
          ctx.globalAlpha = isHovered ? 0.5 : 0.3;
          ctx.fillRect(x, y, width, height);
          
          // Border when selected
          if (isSelected) {
            ctx.strokeStyle = '#2196F3';
            ctx.lineWidth = 2;
            ctx.globalAlpha = 1;
            ctx.strokeRect(x, y, width, height);
          }
          break;

        case AnnotationType.REDACTION:
          // Solid black redaction
          ctx.fillStyle = '#000000';
          ctx.globalAlpha = 1;
          ctx.fillRect(x, y, width, height);
          
          // Border when selected
          if (isSelected) {
            ctx.strokeStyle = '#F44336';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, width, height);
          }
          break;

        case AnnotationType.STICKY_NOTE:
          // Note icon background
          ctx.fillStyle = color;
          ctx.globalAlpha = isHovered ? 0.9 : 0.8;
          ctx.fillRect(x, y, 30, 30);
          
          // Note icon border
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1;
          ctx.globalAlpha = 1;
          ctx.strokeRect(x, y, 30, 30);
          
          // Selection indicator
          if (isSelected) {
            ctx.strokeStyle = '#2196F3';
            ctx.lineWidth = 3;
            ctx.strokeRect(x - 2, y - 2, 34, 34);
          }
          break;
      }

      ctx.restore();
    });

    // Draw current drawing rectangle
    if (isDrawing && currentRect && startPos) {
      ctx.save();
      ctx.strokeStyle = selectedColor;
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      
      if (selectedTool === AnnotationType.REDACTION) {
        ctx.fillStyle = '#000000';
        ctx.globalAlpha = 0.5;
        ctx.fillRect(
          currentRect.x * scale,
          currentRect.y * scale,
          currentRect.width * scale,
          currentRect.height * scale
        );
      } else if (selectedTool === AnnotationType.HIGHLIGHT) {
        ctx.fillStyle = selectedColor;
        ctx.globalAlpha = 0.3;
        ctx.fillRect(
          currentRect.x * scale,
          currentRect.y * scale,
          currentRect.width * scale,
          currentRect.height * scale
        );
      }
      
      ctx.strokeRect(
        currentRect.x * scale,
        currentRect.y * scale,
        currentRect.width * scale,
        currentRect.height * scale
      );
      ctx.restore();
    }
  }, [pageAnnotations, scale, isDrawing, currentRect, startPos, selectedColor, selectedTool, hoveredAnnotation, selectedAnnotation]);

  /**
   * Redraw canvas when annotations change
   */
  useEffect(() => {
    drawAnnotations();
  }, [drawAnnotations]);

  /**
   * Get annotation at position
   */
  const getAnnotationAt = (x: number, y: number): Annotation | null => {
    // Check in reverse order (top annotations first)
    for (let i = pageAnnotations.length - 1; i >= 0; i--) {
      const annotation = pageAnnotations[i];
      const pos = annotation.position;
      
      const scaledX = pos.x * scale;
      const scaledY = pos.y * scale;
      const scaledWidth = annotation.type === AnnotationType.STICKY_NOTE ? 30 : pos.width * scale;
      const scaledHeight = annotation.type === AnnotationType.STICKY_NOTE ? 30 : pos.height * scale;
      
      if (
        x >= scaledX &&
        x <= scaledX + scaledWidth &&
        y >= scaledY &&
        y <= scaledY + scaledHeight
      ) {
        return annotation;
      }
    }
    return null;
  };

  /**
   * Handle mouse down - start drawing
   */
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!selectedTool) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / scale;
    const y = (e.clientY - rect.top) / scale;

    // Check if clicking on existing annotation
    const clickedAnnotation = getAnnotationAt(e.clientX - rect.left, e.clientY - rect.top);
    if (clickedAnnotation) {
      setSelectedAnnotation(clickedAnnotation.id);
      onAnnotationSelect?.(clickedAnnotation.id);
      
      // Show note content for sticky notes
      if (clickedAnnotation.type === AnnotationType.STICKY_NOTE) {
        setNoteContent(clickedAnnotation.content || '');
        setNotePosition(clickedAnnotation.position);
        setShowNoteDialog(true);
      }
      return;
    }

    // Start drawing new annotation
    if (selectedTool === AnnotationType.STICKY_NOTE) {
      // Sticky note: single click
      setNotePosition({ x, y, width: 30, height: 30 });
      setNoteContent('');
      setShowNoteDialog(true);
    } else {
      // Highlight/Redaction: drag to draw
      setIsDrawing(true);
      setStartPos({ x, y });
      setCurrentRect({ x, y, width: 0, height: 0 });
    }
  };

  /**
   * Handle mouse move - update drawing
   */
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Update cursor based on hover
    const hoveredAnn = getAnnotationAt(mouseX, mouseY);
    if (hoveredAnn) {
      canvas.style.cursor = 'pointer';
      setHoveredAnnotation(hoveredAnn.id);
    } else {
      canvas.style.cursor = selectedTool ? 'crosshair' : 'default';
      setHoveredAnnotation(null);
    }

    // Update drawing rectangle
    if (isDrawing && startPos) {
      const x = mouseX / scale;
      const y = mouseY / scale;
      
      const rectX = Math.min(startPos.x, x);
      const rectY = Math.min(startPos.y, y);
      const rectWidth = Math.abs(x - startPos.x);
      const rectHeight = Math.abs(y - startPos.y);
      
      setCurrentRect({
        x: rectX,
        y: rectY,
        width: rectWidth,
        height: rectHeight,
      });
    }
  };

  /**
   * Handle mouse up - finish drawing
   */
  const handleMouseUp = () => {
    if (!isDrawing || !currentRect || !startPos || !selectedTool) return;

    // Only create annotation if rectangle has minimum size
    if (currentRect.width > 10 && currentRect.height > 10) {
      onAnnotationCreate({
        documentId,
        type: selectedTool,
        pageNumber,
        position: currentRect,
        color: selectedColor,
      });
    }

    // Reset drawing state
    setIsDrawing(false);
    setStartPos(null);
    setCurrentRect(null);
  };

  /**
   * Handle note save
   */
  const handleNoteSave = () => {
    if (!notePosition) return;

    onAnnotationCreate({
      documentId,
      type: AnnotationType.STICKY_NOTE,
      pageNumber,
      position: notePosition,
      content: noteContent,
      color: selectedColor,
    });

    setShowNoteDialog(false);
    setNoteContent('');
    setNotePosition(null);
  };

  /**
   * Handle annotation delete
   */
  const handleDelete = () => {
    if (selectedAnnotation) {
      onAnnotationDelete(selectedAnnotation);
      setSelectedAnnotation(null);
      onAnnotationSelect?.(null);
    }
  };

  return (
    <div
      ref={overlayRef}
      className="absolute inset-0 pointer-events-auto"
      style={{
        width: pageWidth * scale,
        height: pageHeight * scale,
      }}
    >
      {/* Canvas for drawing annotations */}
      <canvas
        ref={canvasRef}
        width={pageWidth * scale}
        height={pageHeight * scale}
        className="absolute inset-0"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => {
          setIsDrawing(false);
          setHoveredAnnotation(null);
        }}
        style={{
          cursor: selectedTool ? 'crosshair' : 'default',
        }}
      />

      {/* Sticky Note Dialog */}
      {showNoteDialog && notePosition && (
        <div
          className="absolute z-50 bg-white rounded-lg shadow-xl border border-gray-300 p-4"
          style={{
            left: notePosition.x * scale + 40,
            top: notePosition.y * scale,
            minWidth: '250px',
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <MessageSquareIcon className="w-4 h-4 text-gray-600" />
              <h3 className="font-semibold text-sm">Nota</h3>
            </div>
            <button
              onClick={() => {
                setShowNoteDialog(false);
                setNoteContent('');
                setNotePosition(null);
              }}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <XIcon className="w-4 h-4" />
            </button>
          </div>
          
          <textarea
            value={noteContent}
            onChange={(e) => setNoteContent(e.target.value)}
            placeholder="Escribe tu nota aquí..."
            className="w-full px-3 py-2 border border-gray-300 rounded text-sm resize-none"
            rows={4}
            autoFocus
          />
          
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={() => {
                setShowNoteDialog(false);
                setNoteContent('');
                setNotePosition(null);
              }}
              className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded"
            >
              Cancelar
            </button>
            <button
              onClick={handleNoteSave}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Guardar
            </button>
          </div>
        </div>
      )}

      {/* Delete button for selected annotation */}
      {selectedAnnotation && !showNoteDialog && (
        <button
          onClick={handleDelete}
          className="absolute top-2 right-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 shadow-lg z-50"
        >
          Eliminar anotación
        </button>
      )}
    </div>
  );
};

export default AnnotationLayer;
