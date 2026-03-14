import { useEffect, useRef } from 'react'
import '../App.css'

export default function ThoughtLog({ thoughts, running }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [thoughts])

  return (
    <div className="thought-panel">
      <div className="thought-header">
        <span>⚡</span>
        Agent Thoughts
        {running && <span style={{marginLeft:'auto', color:'var(--teal)'}}>● live</span>}
      </div>
      <div className="thought-log">
        {thoughts.length === 0 ? (
          <div className="thought-empty">
            Waiting for task...<br />
            Iris will show her<br />
            thinking here.
          </div>
        ) : (
          thoughts.map((t, i) => (
            <div key={i} className={`thought-item ${t.done ? 'done' : ''}`}>
              <div className="thought-step">Step {t.step}</div>
              <div className="thought-text">{t.thought}</div>
              <div className="thought-action">⚡ {t.action}</div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}