import React, { useState, useRef, useCallback, useEffect } from 'react';

interface ResizableLayoutProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  initialLeftWidth?: number; 
  minLeftWidth?: number;
  maxLeftWidth?: number; 
  height?: string;
  gap?: number;
}

const ResizableLayout: React.FC<ResizableLayoutProps> = ({
  leftPanel,
  rightPanel,
  initialLeftWidth = 50,
  minLeftWidth = 20,
  maxLeftWidth = 80,
  height = 'calc(100vh - 400px)',
  gap = 24
}) => {
  const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width - gap; 
    const mouseX = e.clientX - containerRect.left;
    
    
    const newLeftWidth = Math.min(
      Math.max((mouseX / containerWidth) * 100, minLeftWidth),
      maxLeftWidth
    );
    
    setLeftWidth(newLeftWidth);
  }, [isDragging, gap, minLeftWidth, maxLeftWidth]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const rightWidth = 100 - leftWidth;

  return (
    <div
      ref={containerRef}
      style={{
        display: 'flex',
        height,
        position: 'relative',
        width: '100%'
      }}
    >
      <div
        style={{
          width: `${leftWidth}%`,
          overflow: 'auto',
          transition: isDragging ? 'none' : 'width 0.1s ease'
        }}
      >
        {leftPanel}
      </div>

      <div
        onMouseDown={handleMouseDown}
        style={{
          width: gap,
          cursor: 'col-resize',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: isDragging ? '#e6f7ff' : 'transparent',
          borderLeft: isDragging ? '2px solid #1890ff' : '1px solid transparent',
          borderRight: isDragging ? '2px solid #1890ff' : '1px solid transparent',
          transition: 'all 0.2s ease',
          position: 'relative',
          zIndex: 10
        }}
        onMouseEnter={(e) => {
          if (!isDragging) {
            e.currentTarget.style.background = '#f0f0f0';
            e.currentTarget.style.borderLeft = '1px solid #d9d9d9';
            e.currentTarget.style.borderRight = '1px solid #d9d9d9';
          }
        }}
        onMouseLeave={(e) => {
          if (!isDragging) {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.borderLeft = '1px solid transparent';
            e.currentTarget.style.borderRight = '1px solid transparent';
          }
        }}
      >
        <div
          style={{
            width: 4,
            height: 40,
            background: isDragging ? '#1890ff' : '#bfbfbf',
            borderRadius: 2,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            transition: 'background 0.2s ease'
          }}
        >
          <div
            style={{
              width: 2,
              height: 2,
              background: 'white',
              borderRadius: '50%',
              marginBottom: 2
            }}
          />
          <div
            style={{
              width: 2,
              height: 2,
              background: 'white',
              borderRadius: '50%',
              marginBottom: 2
            }}
          />
          <div
            style={{
              width: 2,
              height: 2,
              background: 'white',
              borderRadius: '50%'
            }}
          />
        </div>
      </div>

      <div
        style={{
          width: `${rightWidth}%`,
          overflow: 'auto',
          transition: isDragging ? 'none' : 'width 0.1s ease'
        }}
      >
        {rightPanel}
      </div>
    </div>
  );
};

export default ResizableLayout;