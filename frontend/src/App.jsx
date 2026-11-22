import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default function App() {
  const [mode, setMode] = useState('query')
  const [input, setInput] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function runResearch(e) {
    e.preventDefault()
    if (!input.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, input: input.trim() })
      })
      const data = await response.json()
      if (!response.ok) {
        const detail = typeof data.detail === 'string'
          ? data.detail
          : data.detail?.message
        throw new Error(detail || data.error || 'Request failed')
      }
      setResult(data)
    } catch (err) {
      setError(err.message || 'Could not connect to the backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <header>
        <h1>Noida Area Research</h1>
        <p>AI-assisted research for locations and sectors in Noida.</p>
      </header>

      <section className="panel">
        <h2>Start a research task</h2>
        <form onSubmit={runResearch}>
          <label htmlFor="mode">Input type</label>
          <select id="mode" value={mode} onChange={e => setMode(e.target.value)}>
            <option value="query">Specific query</option>
            <option value="sector">Sector</option>
            <option value="city">City</option>
          </select>

          <label htmlFor="research-input">What would you like to research?</label>
          <textarea
            id="research-input"
            rows="3"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={
              mode === 'sector' ? 'Example: Sector 62' :
              mode === 'city' ? 'Example: Noida' :
              'Example: Check infrastructure and connectivity around Sector 62'
            }
          />

          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? 'Processing...' : 'Run research'}
          </button>
        </form>
        <p className="hint">The system will create a plan, run its selected tools, and return source results.</p>
      </section>

      {error && <section className="panel error"><strong>Error:</strong> {error}</section>}

      {result && (
        <section className="panel">
          <h2>Research output</h2>
          <p><strong>Status:</strong> {result.status || 'Completed'}</p>
          {result.run_id && <p><strong>Run ID:</strong> <code>{result.run_id}</code></p>}

          {result.intent && (
            <>
              <h3>Detected intent</h3>
              <p><strong>City:</strong> {result.intent.city || 'Noida'}</p>
              {result.intent.sector && <p><strong>Sector:</strong> {result.intent.sector}</p>}
              {result.intent.topic?.length > 0 && <p><strong>Topics:</strong> {result.intent.topic.join(', ')}</p>}
            </>
          )}

          {result.research_plan && (
            <>
              <h3>Research plan</h3>
              <p>{result.research_plan.location_scope}</p>
              <p><strong>Tools:</strong> {(result.research_plan.selected_tools || []).join(', ') || 'None selected'}</p>
              {result.research_plan.research_questions?.length > 0 && (
                <ul>{result.research_plan.research_questions.map((q, i) => <li key={i}>{q}</li>)}</ul>
              )}
            </>
          )}

          {result.tool_results?.length > 0 && (
            <>
              <h3>Research results</h3>
              {result.tool_results.map((toolResult, index) => {
                const data = toolResult.data || {}

                return (
                  <article className="tool-result" key={`${toolResult.tool}-${index}`}>
                    <h4>{toolResult.tool.replaceAll('_', ' ')} · {toolResult.status}</h4>
                    {data.provider && <p><strong>Source:</strong> {data.provider}</p>}
                    {data.answer && <p>{data.answer}</p>}
                    {toolResult.error && <p className="error-message">{toolResult.error}</p>}

                    {data.current && (
                      <p>
                        <strong>Current weather:</strong>{' '}
                        {data.current.temperature_2m}{data.current_units?.temperature_2m},{' '}
                        feels like {data.current.apparent_temperature}{data.current_units?.apparent_temperature},
                        {' '}{data.current.relative_humidity_2m}% humidity
                      </p>
                    )}

                    {data.daily?.time?.length > 0 && (
                      <ul>
                        {data.daily.time.map((date, dayIndex) => (
                          <li key={date}>
                            {date}: {data.daily.temperature_2m_min?.[dayIndex]}–
                            {data.daily.temperature_2m_max?.[dayIndex]}{data.daily_units?.temperature_2m_max},
                            {' '}precipitation chance {data.daily.precipitation_probability_max?.[dayIndex]}%
                          </li>
                        ))}
                      </ul>
                    )}

                    {data.results?.length > 0 && (
                      <ul>
                        {data.results.map((item, resultIndex) => {
                          const resultUrl = /^https?:\/\//i.test(item.url || '')
                            ? item.url
                            : null

                          return (
                            <li key={resultUrl || resultIndex}>
                              {resultUrl ? (
                                <a href={resultUrl} target="_blank" rel="noopener noreferrer">
                                  {item.title || item.url}
                                </a>
                              ) : item.title}
                              {item.published_date && <small> · {item.published_date}</small>}
                              {item.content && <p>{item.content}</p>}
                            </li>
                          )
                        })}
                      </ul>
                    )}
                  </article>
                )
              })}
            </>
          )}

          {result.errors?.length > 0 && (
            <div className="error-message">
              <strong>Some tools could not complete:</strong>
              <ul>{result.errors.map((item, index) => <li key={index}>{item}</li>)}</ul>
            </div>
          )}

          {result.execution_trace?.length > 0 && (
            <>
              <h3>Execution log</h3>
              <ul>{result.execution_trace.map((item, i) => <li key={i}>{item}</li>)}</ul>
            </>
          )}
        </section>
      )}

      <footer>Prototype · Noida, India</footer>
    </main>
  )
}