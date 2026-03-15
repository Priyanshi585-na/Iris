import { useState, useEffect, useRef } from 'react'
import BrowserStream from './Components/Browser'
import ThoughtLog from './Components/Thoughtlog'
import TaskInput from './Components/TaskInput'
import logo from '/iris.svg'

const WS_URL = 'wss://trena-statistical-zander.ngrok-free.dev/ws'
const NOVNC_URL = 'https://trena-statistical-zander.ngrok-free.dev/novnc?autoconnect=true&reconnect=true&resize=scale'

export default function App() {
  const [connected, setConnected] = useState(false)
  const [running, setRunning] = useState(false)
  const [thoughts, setThoughts] = useState([])
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('Connecting...')
  const ws = useRef(null)

  useEffect(() => {
    connect()
    return () => ws.current?.close()
  }, [])

  const connect = () => {
    ws.current = new WebSocket(WS_URL)

    ws.current.onopen = () => {
      setConnected(true)
      setStatus('Ready')
    }

    ws.current.onclose = () => {
      setConnected(false)
      setStatus('Disconnected')
      setTimeout(connect, 3000)
    }

    ws.current.onmessage = (e) => {
      const msg = JSON.parse(e.data)

      if (msg.type === 'step') {
        setThoughts(prev => [...prev, {
          step: msg.step,
          thought: msg.thought,
          action: msg.action,
          done: msg.action === 'done'
        }])
        setStatus(`Step ${msg.step} — ${msg.action}`)
      }

      if (msg.type === 'done') {
        setResult(msg.result)
        setRunning(false)
        setStatus('Ready')
      }

      if (msg.type === 'status') {
        setStatus(msg.message)
      }
    }
  }

  const runTask = (task) => {
    if (!connected || !task.trim()) return
    setThoughts([])
    setResult(null)
    setRunning(true)
    setStatus('Starting...')
    ws.current.send(JSON.stringify({ type: 'task', task }))
  }

  const stopTask = () => {
    ws.current?.send(JSON.stringify({ type: 'stop' }))
    setRunning(false)
    setStatus('Stopped')
  }

  return (
    <div className="iris-app">
      {/* Header */}
      <header className="iris-header">
        <div className="iris-logo">
          <div className="iris-eye-container">
            <div className="iris-eye-ring" />
            <div className="iris-eye-ring iris-eye-ring--2" />
            <div className="iris-eye-core">
              <img src={logo} alt="Iris" className="logo" />
            </div>
          </div>
          <div>
            <div className="iris-logo-text">Iris</div>
          </div>
        </div>
        <div className="iris-tagline">See the web. So you don't have to.</div>
        <div className="status-badge">
          <div className={`status-dot ${connected ? '' : 'offline'}`} />
          {status}
        </div>
      </header>

      <main className="iris-main">
        <BrowserStream url={NOVNC_URL} running={running} />

        <ThoughtLog thoughts={thoughts} running={running} />

        <TaskInput
          onRun={runTask}
          onStop={stopTask}
          running={running}
          connected={connected}
          result={result}
        />
      </main>
    </div>
  )
}