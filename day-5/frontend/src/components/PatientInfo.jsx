import React, { useState } from 'react';
import './PatientInfo.css';

function PatientInfo({ patientData, onPatientChange, specialty, onSpecialtyChange }) {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState(patientData || {});

  const handleInputChange = (field, value) => {
    const updated = { ...formData, [field]: value };
    setFormData(updated);
  };

  const handleArrayChange = (field, value) => {
    const items = value
      .split(',')
      .map(item => item.trim())
      .filter(item => item);
    handleInputChange(field, items);
  };

  const handleSave = () => {
    onPatientChange(formData);
    setShowForm(false);
  };

  const specialties = [
    { value: 'general_practice', label: '👨‍⚕️ General Practice' },
    { value: 'cardiology', label: '❤️ Cardiology' },
    { value: 'neurology', label: '🧠 Neurology' },
    { value: 'dermatology', label: '🩹 Dermatology' },
    { value: 'pediatrics', label: '👶 Pediatrics' },
    { value: 'psychiatry', label: '💭 Psychiatry' }
  ];

  return (
    <div className="patient-info">
      <h3>👤 Patient Context</h3>

      <div className="specialty-selector">
        <label>Medical Specialty:</label>
        <select value={specialty} onChange={(e) => onSpecialtyChange(e.target.value)}>
          {specialties.map(spec => (
            <option key={spec.value} value={spec.value}>
              {spec.label}
            </option>
          ))}
        </select>
      </div>

      {patientData ? (
        <div className="patient-display">
          <div className="info-item">
            <strong>Name:</strong> {patientData.name}
          </div>
          <div className="info-item">
            <strong>Age:</strong> {patientData.age} years
          </div>
          {patientData.conditions && patientData.conditions.length > 0 && (
            <div className="info-item">
              <strong>Conditions:</strong>
              <ul>
                {patientData.conditions.map((cond, i) => (
                  <li key={i}>{cond}</li>
                ))}
              </ul>
            </div>
          )}
          {patientData.medications && patientData.medications.length > 0 && (
            <div className="info-item">
              <strong>Medications:</strong>
              <ul>
                {patientData.medications.map((med, i) => (
                  <li key={i}>{med}</li>
                ))}
              </ul>
            </div>
          )}
          {patientData.allergies && patientData.allergies.length > 0 && (
            <div className="info-item">
              <strong>Allergies:</strong>
              <ul>
                {patientData.allergies.map((allergy, i) => (
                  <li key={i}>{allergy}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="empty-patient">
          <p>No patient selected</p>
        </div>
      )}

      <button
        className="edit-button"
        onClick={() => {
          setShowForm(!showForm);
          setFormData(patientData || {});
        }}
      >
        {showForm ? '❌ Cancel' : '✏️ Edit Patient'}
      </button>

      {showForm && (
        <div className="patient-form">
          <div className="form-group">
            <label>Patient ID:</label>
            <input
              type="text"
              value={formData.patient_id || ''}
              onChange={(e) => handleInputChange('patient_id', e.target.value)}
              placeholder="P001"
            />
          </div>
          <div className="form-group">
            <label>Name:</label>
            <input
              type="text"
              value={formData.name || ''}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Patient Name"
            />
          </div>
          <div className="form-group">
            <label>Age:</label>
            <input
              type="number"
              value={formData.age || ''}
              onChange={(e) => handleInputChange('age', parseInt(e.target.value))}
              placeholder="45"
            />
          </div>
          <div className="form-group">
            <label>Gender:</label>
            <select value={formData.gender || ''} onChange={(e) => handleInputChange('gender', e.target.value)}>
              <option value="">Select...</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label>Conditions (comma-separated):</label>
            <textarea
              value={(formData.conditions || []).join(', ')}
              onChange={(e) => handleArrayChange('conditions', e.target.value)}
              placeholder="Hypertension, Type 2 Diabetes"
              rows="2"
            />
          </div>
          <div className="form-group">
            <label>Medications (comma-separated):</label>
            <textarea
              value={(formData.medications || []).join(', ')}
              onChange={(e) => handleArrayChange('medications', e.target.value)}
              placeholder="Lisinopril 10mg daily, Metformin 500mg BID"
              rows="2"
            />
          </div>
          <div className="form-group">
            <label>Allergies (comma-separated):</label>
            <textarea
              value={(formData.allergies || []).join(', ')}
              onChange={(e) => handleArrayChange('allergies', e.target.value)}
              placeholder="Penicillin, NSAIDs"
              rows="2"
            />
          </div>
          <button type="button" className="save-button" onClick={handleSave}>
            💾 Save Patient
          </button>
        </div>
      )}
    </div>
  );
}

export default PatientInfo;
