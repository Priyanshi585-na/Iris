import '../App.css'

export default function BrowserStream({ url, running }) {
  return (
    <div className="stream-panel">
      <div className="stream-header">
        <div className="stream-dots">
          <span /><span /><span />
        </div>
        <div className="stream-url">
          {running ? '🔴 Agent controlling browser...' : 'iris-vm — live browser stream'}
        </div>
      </div>
      <div className="stream-body">
        <iframe
          src={url}
          title="Iris Browser Stream"
          allow="fullscreen"
        />
      </div>
    </div>
  )
}