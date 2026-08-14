import React, { useEffect, useState } from 'react';

// Helper component to render a single sub-cube for the 2x2x2 compound structure
const SubCube = ({ x, y, z, size }: { x: number, y: number, z: number, size: number }) => (
  <div className="iso-sub-cube" style={{ 
    width: `${size}px`, height: `${size}px`, 
    transform: `translate3d(${x}px, ${y}px, ${z}px)` 
  }}>
    <div className="iso-sub-face sub-top"></div>
    <div className="iso-sub-face sub-left"></div>
    <div className="iso-sub-face sub-right"></div>
  </div>
);

export const IsometricScene: React.FC = () => {
  const cubeSize = 35; // Size of each of the 8 smaller cubes
  const [truckPos, setTruckPos] = useState({ x: 0, y: 0 });

  // Simulate truck moving along the path
  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t = (t + 1) % 400;
      
      // Define path waypoints relative to the red line path
      if (t < 100) {
        setTruckPos({ x: 200, y: 150 + (t * 1.0) });
      } else if (t < 200) {
        setTruckPos({ x: 200 - ((t - 100) * 0.5), y: 250 });
      } else if (t < 300) {
        setTruckPos({ x: 150, y: 250 - ((t - 200) * 1.0) });
      } else {
        setTruckPos({ x: 150 + ((t - 300) * 0.5), y: 150 });
      }
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="isometric-container">
      <div className="isometric-scene">
        
        {/* Ground Base Grid */}
        <div className="iso-block iso-grid-base" style={{ width: '300px', height: '300px', transform: 'translateZ(-20px)' }}>
          <div className="iso-face iso-top iso-grid-top"></div>
          <div className="iso-face iso-left"></div>
          <div className="iso-face iso-right"></div>
        </div>

        {/* The Red Logistics Path */}
        <div className="iso-path">
          <div className="iso-path-line iso-path-h" style={{ left: '200px', top: '150px', width: '100px' }}></div>
          <div className="iso-path-line iso-path-v" style={{ left: '200px', top: '150px', height: '100px' }}></div>
          <div className="iso-path-line iso-path-h" style={{ left: '150px', top: '250px', width: '50px' }}></div>
        </div>

        {/* Left Side: The 2x2x2 Floating Translucent Red Cube */}
        <div className="iso-compound-cube">
          {/* Bottom Layer */}
          <SubCube x={0} y={0} z={0} size={cubeSize} />
          <SubCube x={cubeSize} y={0} z={0} size={cubeSize} />
          <SubCube x={0} y={cubeSize} z={0} size={cubeSize} />
          <SubCube x={cubeSize} y={cubeSize} z={0} size={cubeSize} />
          {/* Top Layer */}
          <SubCube x={0} y={0} z={cubeSize} size={cubeSize} />
          <SubCube x={cubeSize} y={0} z={cubeSize} size={cubeSize} />
          <SubCube x={0} y={cubeSize} z={cubeSize} size={cubeSize} />
          <SubCube x={cubeSize} y={cubeSize} z={cubeSize} size={cubeSize} />
        </div>

        {/* Top/Back: Solid White Floating Cube */}
        <div className="iso-block iso-floating-white" style={{ width: '80px', height: '80px', top: '0', left: '150px' }}>
          <div className="iso-face iso-top" style={{ transform: 'translateZ(80px)' }}></div>
          <div className="iso-face iso-left" style={{ height: '80px', transform: 'rotateY(-90deg) translateZ(40px) translateX(-40px)' }}></div>
          <div className="iso-face iso-right" style={{ height: '80px', transform: 'rotateX(-90deg) translateZ(40px) translateY(40px)' }}></div>
        </div>

        {/* Bottom Right: Red/Blue Warehouse SVG */}
        <div className="iso-red-warehouse" style={{ position: 'absolute', top: '190px', left: '100px', transformStyle: 'preserve-3d', transform: 'translateZ(10px) rotateX(90deg) rotateY(45deg)' }}>
          <svg width="100" height="100" viewBox="0 0 100 100" style={{ filter: 'drop-shadow(2px 5px 3px rgba(0,0,0,0.2))' }}>
            {/* Left Wall (Darker Red) */}
            <polygon points="10,60 50,80 50,40 10,20" fill="#b31b1b" />
            {/* Right Wall (Red) */}
            <polygon points="50,80 90,60 90,20 50,40" fill="#d32f2f" />
            
            {/* Roof (Curved Blue) */}
            <path d="M 10,20 Q 30,-5 50,15 L 90,35 Q 70,10 50,40 Z" fill="#1976d2" />
            <path d="M 10,20 Q 30,-5 50,15" fill="none" stroke="#0d47a1" strokeWidth="1" />
            
            {/* Garage Door (White) */}
            <polygon points="15,58 45,73 45,55 15,40" fill="#f5f5f5" />
            <polygon points="15,58 45,73 45,55 15,40" fill="none" stroke="#cccccc" strokeWidth="0.5" />
            {/* Garage Door Lines */}
            <line x1="16" y1="44" x2="44" y2="58" stroke="#cccccc" strokeWidth="0.5" />
            <line x1="16" y1="48" x2="44" y2="62" stroke="#cccccc" strokeWidth="0.5" />
            <line x1="16" y1="52" x2="44" y2="66" stroke="#cccccc" strokeWidth="0.5" />
            <line x1="16" y1="56" x2="44" y2="70" stroke="#cccccc" strokeWidth="0.5" />

            {/* Side Windows */}
            <polygon points="55,55 65,50 65,45 55,50" fill="#424242" />
            <polygon points="70,47 80,42 80,37 70,42" fill="#424242" />

            {/* WAREHOUSE Text */}
            <text x="25" y="38" fill="white" fontSize="6" fontWeight="bold" transform="matrix(0.89 0.45 0 1 0 0)">WAREHOUSE</text>
          </svg>
        </div>

        {/* Bottom Right: 2D Crane (Animated) */}
        <div className="iso-crane" style={{ left: `${truckPos.x - 12}px`, top: `${truckPos.y - 20}px` }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ff5733" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {/* Base */}
            <line x1="3" y1="21" x2="21" y2="21"></line>
            <line x1="12" y1="21" x2="12" y2="6"></line>
            {/* Arm */}
            <polyline points="4 9 12 5 22 9"></polyline>
            {/* Hook */}
            <line x1="20" y1="9" x2="20" y2="17"></line>
            <path d="M18 17a2 2 0 1 0 4 0"></path>
          </svg>
        </div>

      </div>
    </div>
  );
};

