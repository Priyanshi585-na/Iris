import { useState } from 'react'
import '../App.css'

const SUGGESTIONS = [
  'Search best laptops under ₹50,000 on Flipkart',
  'Go to Wikipedia and summarize Quantum Computing',
  'Find restaurants in Mumbai on Zomato',
  'Search for iPhone 16 on Amazon India',
]

export default function TaskInput({ onRun, onStop, running, connected, result }) {
  const [task, setTask] = useState('')

  const handleRun = () => {
    if (task.trim()) onRun(task)
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleRun()
    }
  }

  return (
    <div className="task-panel">
      <div className="task-label">⌨ Give Iris a task</div>
      <div className="task-input-wrapper">
        <textarea
          className="task-input"
          placeholder="e.g. Find best shoes under ₹1000 on Flipkart..."
          value={task}
          onChange={e => setTask(e.target.value)}
          onKeyDown={handleKey}
          disabled={running}
          rows={1}
        />
        {running ? (
          <button className="stop-btn" onClick={onStop}>⏹ Stop</button>
        ) : (
          <button
            className="run-btn"
            onClick={handleRun}
            disabled={!connected || !task.trim()}
          >
            Run ▶
          </button>
        )}
      </div>

      {/* Suggestion chips */}
      {!running && (
        <div className="suggestions">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              className="suggestion-chip"
              onClick={() => setTask(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="result-box">
          <div className="result-label">✅ Iris says</div>
          {result}
        </div>
      )}
    </div>
  )
}