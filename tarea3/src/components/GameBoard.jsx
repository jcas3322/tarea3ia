import { useState } from 'react';
import './GameBoard.css';

const GameBoard = () => {
  const [matrix, setMatrix] = useState(null);
  const [isFinished, setIsFinished] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const startGame = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/start');
      const data = await response.json();
      setMatrix(data.board);
      setIsFinished(data.finished);
    } catch (error) {
      console.error('Error al iniciar el juego:', error);
    }
    setIsLoading(false);
  };

  const nextIteration = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/next');
      const data = await response.json();
      setMatrix(data.board);
      setIsFinished(data.finished);
    } catch (error) {
      console.error('Error al obtener siguiente iteración:', error);
    }
    setIsLoading(false);
  };

  return (
    <div className="game-container">
      <h1>Juego del 8</h1>
      <div className="board">
        {matrix && matrix.map((row, i) => (
          <div key={i} className="row">
            {row.map((cell, j) => (
              <div 
                key={`${i}-${j}`} 
                className={`cell ${cell === 0 ? 'empty' : ''}`}
              >
                {cell !== 0 && cell}
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="controls">
        <button 
          onClick={startGame} 
          disabled={isLoading || (!isFinished && matrix)}
          className="button"
        >
          Empezar
        </button>
        <button 
          onClick={nextIteration} 
          disabled={isLoading || !matrix || isFinished}
          className="button"
        >
          Siguiente
        </button>
      </div>
      {isFinished && (
        <div className="finished">
          ¡Juego terminado!
        </div>
      )}
    </div>
  );
};

export default GameBoard; 