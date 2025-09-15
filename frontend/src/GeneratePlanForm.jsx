import { useState } from 'react'
import './GeneratePlanForm.css' // CSS for centering and styling

function GeneratePlanForm() {
  const [brandUrl, setBrandUrl] = useState('')
  const [competitorUrl, setCompetitorUrl] = useState('')
  const [locations, setLocations] = useState('')
  const [shoppingBudget, setShoppingBudget] = useState('')
  const [searchBudget, setSearchBudget] = useState('')
  const [pmaxBudget, setPmaxBudget] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const payload = {
      brand_url: brandUrl,
      competitor_url: competitorUrl,
      locations: locations.split(',').map(loc => loc.trim()),
      budgets: {
        shopping: Number(shoppingBudget),
        search: Number(searchBudget),
        pmax: Number(pmaxBudget)
      }
    }

    try {
        const res = await fetch('https://sem-planning-tool.onrender.com/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      setResponse(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="form-container">
      <div className="generate-form-container">
        <h1>Generate SEM Plan</h1>
        <form className="generate-form" onSubmit={handleSubmit}>
          <input type="text" placeholder="Brand URL" value={brandUrl} onChange={e => setBrandUrl(e.target.value)} />
          <input type="text" placeholder="Competitor URL" value={competitorUrl} onChange={e => setCompetitorUrl(e.target.value)} />
          <input type="text" placeholder="Locations (comma separated)" value={locations} onChange={e => setLocations(e.target.value)} />
          <input type="number" placeholder="Shopping Budget" value={shoppingBudget} onChange={e => setShoppingBudget(e.target.value)} />
          <input type="number" placeholder="Search Budget" value={searchBudget} onChange={e => setSearchBudget(e.target.value)} />
          <input type="number" placeholder="PMax Budget" value={pmaxBudget} onChange={e => setPmaxBudget(e.target.value)} />
          <button type="submit" disabled={loading}>
            {loading ? "Generating..." : "Generate Plan"}
          </button>
        </form>

        {response && (
          <div>
            <h2>Response:</h2>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default GeneratePlanForm
