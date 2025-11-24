import React, { useState, FormEvent } from 'react'
import './JobSearchForm.css'

interface SalaryRange {
  min: number | ''
  max: number | ''
}

interface FormData {
  receiverEmails: string[]
  locations: string[]
  salaryRanges: SalaryRange[]
  experienceMin: number | ''
  experienceMax: number | ''
  jobTitle: string
}

const JobSearchForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    receiverEmails: [''],
    locations: [''],
    salaryRanges: [{ min: '', max: '' }],
    experienceMin: '',
    experienceMax: '',
    jobTitle: '',
  })

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const addEmail = () => {
    setFormData({
      ...formData,
      receiverEmails: [...formData.receiverEmails, ''],
    })
  }

  const removeEmail = (index: number) => {
    if (formData.receiverEmails.length > 1) {
      setFormData({
        ...formData,
        receiverEmails: formData.receiverEmails.filter((_, i) => i !== index),
      })
    }
  }

  const updateEmail = (index: number, value: string) => {
    const newEmails = [...formData.receiverEmails]
    newEmails[index] = value
    setFormData({ ...formData, receiverEmails: newEmails })
  }

  const addLocation = () => {
    setFormData({
      ...formData,
      locations: [...formData.locations, ''],
    })
  }

  const removeLocation = (index: number) => {
    if (formData.locations.length > 1) {
      setFormData({
        ...formData,
        locations: formData.locations.filter((_, i) => i !== index),
      })
    }
  }

  const updateLocation = (index: number, value: string) => {
    const newLocations = [...formData.locations]
    newLocations[index] = value
    setFormData({ ...formData, locations: newLocations })
  }

  const addSalaryRange = () => {
    setFormData({
      ...formData,
      salaryRanges: [...formData.salaryRanges, { min: '', max: '' }],
    })
  }

  const removeSalaryRange = (index: number) => {
    if (formData.salaryRanges.length > 1) {
      setFormData({
        ...formData,
        salaryRanges: formData.salaryRanges.filter((_, i) => i !== index),
      })
    }
  }

  const updateSalaryRange = (index: number, field: 'min' | 'max', value: string) => {
    const newRanges = [...formData.salaryRanges]
    newRanges[index] = {
      ...newRanges[index],
      [field]: value === '' ? '' : Number(value),
    }
    setFormData({ ...formData, salaryRanges: newRanges })
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    // Validate form
    const validEmails = formData.receiverEmails.filter((email) => email.trim() !== '')
    if (validEmails.length === 0) {
      setMessage({ type: 'error', text: 'Please add at least one receiver email' })
      setLoading(false)
      return
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    for (const email of validEmails) {
      if (!emailRegex.test(email)) {
        setMessage({ type: 'error', text: `Invalid email format: ${email}` })
        setLoading(false)
        return
      }
    }

    // Prepare payload
    const payload = {
      receiver_emails: validEmails,
      locations: formData.locations.filter((loc) => loc.trim() !== ''),
      salary_ranges: formData.salaryRanges
        .filter((range) => range.min !== '' || range.max !== '')
        .map((range) => ({
          min: range.min === '' ? 0 : Number(range.min),
          max: range.max === '' ? 999999 : Number(range.max),
        })),
      experience_min: formData.experienceMin === '' ? null : Number(formData.experienceMin),
      experience_max: formData.experienceMax === '' ? null : Number(formData.experienceMax),
      job_title: formData.jobTitle.trim(),
    }

    try {
      const response = await fetch('/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({
          type: 'success',
          text: `Configuration saved successfully! Updated ${data.updated_count} profile(s).`,
        })
        // Reset form after successful submission
        setTimeout(() => {
          setFormData({
            receiverEmails: [''],
            locations: [''],
            salaryRanges: [{ min: '', max: '' }],
            experienceMin: '',
            experienceMax: '',
            jobTitle: '',
          })
          setMessage(null)
        }, 3000)
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to save configuration' })
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="job-search-form">
      {/* Receiver Emails */}
      <div className="form-section">
        <label className="form-label">
          <span className="label-icon">📧</span>
          Receiver Emails *
        </label>
        <div className="multi-input-group">
          {formData.receiverEmails.map((email, index) => (
            <div key={index} className="input-with-button">
              <input
                type="email"
                value={email}
                onChange={(e) => updateEmail(index, e.target.value)}
                placeholder="email@example.com"
                className="form-input"
                required={index === 0}
              />
              {formData.receiverEmails.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeEmail(index)}
                  className="remove-button"
                  aria-label="Remove email"
                >
                  ×
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={addEmail} className="add-button">
            + Add Email
          </button>
        </div>
      </div>

      {/* Locations */}
      <div className="form-section">
        <label className="form-label">
          <span className="label-icon">📍</span>
          Preferred Locations
        </label>
        <div className="multi-input-group">
          {formData.locations.map((location, index) => (
            <div key={index} className="input-with-button">
              <input
                type="text"
                value={location}
                onChange={(e) => updateLocation(index, e.target.value)}
                placeholder="e.g., Bangalore, Mumbai, Remote"
                className="form-input"
              />
              {formData.locations.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeLocation(index)}
                  className="remove-button"
                  aria-label="Remove location"
                >
                  ×
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={addLocation} className="add-button">
            + Add Location
          </button>
        </div>
      </div>

      {/* Salary Ranges */}
      <div className="form-section">
        <label className="form-label">
          <span className="label-icon">💰</span>
          Salary Ranges (LPA)
        </label>
        <div className="salary-ranges">
          {formData.salaryRanges.map((range, index) => (
            <div key={index} className="salary-range-group">
              <div className="salary-inputs">
                <input
                  type="number"
                  value={range.min}
                  onChange={(e) => updateSalaryRange(index, 'min', e.target.value)}
                  placeholder="Min"
                  className="form-input salary-input"
                  min="0"
                />
                <span className="salary-separator">-</span>
                <input
                  type="number"
                  value={range.max}
                  onChange={(e) => updateSalaryRange(index, 'max', e.target.value)}
                  placeholder="Max"
                  className="form-input salary-input"
                  min="0"
                />
                <span className="salary-unit">LPA</span>
              </div>
              {formData.salaryRanges.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeSalaryRange(index)}
                  className="remove-button"
                  aria-label="Remove salary range"
                >
                  ×
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={addSalaryRange} className="add-button">
            + Add Salary Range
          </button>
        </div>
      </div>

      {/* Experience */}
      <div className="form-section">
        <label className="form-label">
          <span className="label-icon">💼</span>
          Experience (Years)
        </label>
        <div className="experience-group">
          <input
            type="number"
            value={formData.experienceMin}
            onChange={(e) =>
              setFormData({ ...formData, experienceMin: e.target.value === '' ? '' : Number(e.target.value) })
            }
            placeholder="Min"
            className="form-input experience-input"
            min="0"
          />
          <span className="experience-separator">-</span>
          <input
            type="number"
            value={formData.experienceMax}
            onChange={(e) =>
              setFormData({ ...formData, experienceMax: e.target.value === '' ? '' : Number(e.target.value) })
            }
            placeholder="Max"
            className="form-input experience-input"
            min="0"
          />
          <span className="experience-unit">years</span>
        </div>
      </div>

      {/* Job Title */}
      <div className="form-section">
        <label className="form-label">
          <span className="label-icon">🔎</span>
          Job Title / Search Query
        </label>
        <input
          type="text"
          value={formData.jobTitle}
          onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
          placeholder="e.g., Software Engineer, React Developer, Python Developer"
          className="form-input"
        />
      </div>

      {/* Message */}
      {message && (
        <div className={`message ${message.type}`}>
          {message.type === 'success' ? '✅' : '❌'} {message.text}
        </div>
      )}

      {/* Submit Button */}
      <button type="submit" className="submit-button" disabled={loading}>
        {loading ? 'Saving...' : '💾 Save Configuration'}
      </button>
    </form>
  )
}

export default JobSearchForm

