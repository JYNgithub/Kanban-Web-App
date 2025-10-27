<template>
  <div class="container">

    <!-- Header -->
    <header class="app-header">
      <h1 class="app-title">CRM Kanban Board</h1>
    </header>

    <!-- Action Section -->
    <section class="action-section">
      <div class="action-container">
        <!-- Add Record Button -->
        <button 
          @click="showAddModal = true" 
          class="add-record-btn"
          :disabled="loading"
        >
          <div class="btn-icon">+</div>
          <span>Add Record</span>
        </button>
      </div>
    </section>
    
    <!-- Kanban Board -->
    <section class="kanban-board">
      <div class="columns-container">
        <!-- New Records -->
        <div class="kanban-column new-column">
          <div class="column-header">
            <div class="column-icon">✨</div>
            <h3>New</h3>
            <div class="record-counter">{{ newRecords.length }}</div>
          </div>
          
          <div class="column-content">
            <Draggable
              :list="newRecords"
              :group="{ name: 'records', pull: true, put: true }"
              item-key="id"
              :animation="300"
              @change="onDrop('New', $event)"
              class="drag-area"
              ghost-class="ghost-card"
              chosen-class="chosen-card"
              drag-class="drag-card"
              :disabled="dragLoading"
            >
              <template #item="{ element }">
                <div 
                  class="record-card" 
                  :key="element.id"
                  @click="openRecordDetails(element)"
                >
                  <div class="card-glow"></div>
                  <div class="record-content">
                    <div class="record-name">{{ element.name }}</div>
                    <div class="record-phone">{{ element.phone_number }}</div>
                    <div class="record-status new-status">New</div>
                  </div>
                  <div class="drag-handle" @click.stop>⋮⋮</div>
                  <div v-if="dragLoading && element.id === currentlyDraggingId" class="drag-loading-overlay">
                    <div class="drag-loading-spinner"></div>
                  </div>
                </div>
              </template>
            </Draggable>
            
            <div v-if="newRecords.length === 0" class="empty-state">
              <div class="empty-icon">📂</div>
              <p>No new records</p>
            </div>
          </div>
        </div>

        <!-- Active Records -->
        <div class="kanban-column active-column">
          <div class="column-header">
            <div class="column-icon">📋</div>
            <h3>Active</h3>
            <div class="record-counter">{{ activeRecords.length }}</div>
          </div>
          
          <div class="column-content">
            <Draggable
              :list="activeRecords"
              :group="{ name: 'records', pull: true, put: true }"
              item-key="id"
              :animation="300"
              @change="onDrop('Active', $event)"
              class="drag-area"
              ghost-class="ghost-card"
              chosen-class="chosen-card"
              drag-class="drag-card"
              :disabled="dragLoading"
            >
              <template #item="{ element }">
                <div 
                  class="record-card" 
                  :key="element.id"
                  @click="openRecordDetails(element)"
                >
                  <div class="card-glow"></div>
                  <div class="record-content">
                    <div class="record-name">{{ element.name }}</div>
                    <div class="record-phone">{{ element.phone_number }}</div>
                    <div class="record-status active-status">Active</div>
                  </div>
                  <div class="drag-handle" @click.stop>⋮⋮</div>
                  <div v-if="dragLoading && element.id === currentlyDraggingId" class="drag-loading-overlay">
                    <div class="drag-loading-spinner"></div>
                  </div>
                </div>
              </template>
            </Draggable>
            
            <div v-if="activeRecords.length === 0" class="empty-state">
              <div class="empty-icon">📂</div>
              <p>No active records</p>
            </div>
          </div>
        </div>

        <!-- Closed Records -->
        <div class="kanban-column closed-column">
          <div class="column-header">
            <div class="column-icon">✅</div>
            <h3>Closed</h3>
            <div class="record-counter">{{ closedRecords.length }}</div>
          </div>
          
          <div class="column-content">
            <Draggable
              :list="closedRecords"
              :group="{ name: 'records', pull: true, put: true }"
              item-key="id"
              :animation="300"
              @change="onDrop('Closed', $event)"
              class="drag-area"
              ghost-class="ghost-card"
              chosen-class="chosen-card"
              drag-class="drag-card"
              :disabled="dragLoading"
            >
              <template #item="{ element }">
                <div 
                  class="record-card closed-card" 
                  :key="element.id"
                  @click="openRecordDetails(element)"
                >
                  <div class="card-glow"></div>
                  <div class="record-content">
                    <div class="record-name">{{ element.name }}</div>
                    <div class="record-phone">{{ element.phone_number }}</div>
                    <div class="record-status closed-status">Closed</div>
                  </div>
                  <div class="drag-handle" @click.stop>⋮⋮</div>
                  <div v-if="dragLoading && element.id === currentlyDraggingId" class="drag-loading-overlay">
                    <div class="drag-loading-spinner"></div>
                  </div>
                </div>
              </template>
            </Draggable>
            
            <div v-if="closedRecords.length === 0" class="empty-state">
              <div class="empty-icon">📂</div>
              <p>No closed records</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- HTML logic: Loading indicator when updating record status -->
    <div v-if="dragLoading" class="global-loading-indicator">
      <div class="global-loading-spinner"></div>
      <span>Updating status...</span>
    </div>

    <!-- HTML logic: Modal form to add records -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <!-- Add loading overlay inside modal -->
        <div v-if="loading" class="modal-loading-overlay">
          <div class="modal-loading-spinner"></div>
          <span>Adding record...</span>
        </div>
        
        <div :class="['modal-content-inner', { 'blurred': loading }]">
          <div class="modal-header">
            <h2>Add New Record</h2>
            <button @click="closeModal" class="close-btn" :disabled="loading">&times;</button>
          </div>
          
          <form @submit.prevent="addRecord" class="record-form">
            <!-- Add the missing form fields -->
            <div class="form-group">
              <label for="name">Name *</label>
              <input 
                type="text" 
                id="name"
                v-model="name" 
                placeholder="Enter full name"
                required
                :disabled="loading"
                autocomplete="off"
              >
            </div>
            
            <div class="form-group">
              <label for="email">Email</label>
              <input 
                type="email" 
                id="email"
                v-model="email" 
                placeholder="Enter email address"
                :disabled="loading"
                autocomplete="off"
              >
            </div>
            
            <div class="form-group">
              <label for="phone">Phone Number</label>
              <input 
                type="tel" 
                id="phone"
                v-model="phone_number" 
                placeholder="Enter phone number"
                :disabled="loading"
                autocomplete="off"
              >
            </div>
            
            <div class="form-group">
              <label for="organization">Organization</label>
              <input 
                type="text" 
                id="organization"
                v-model="organization" 
                placeholder="Enter organization name"
                :disabled="loading"
                autocomplete="off"
              >
            </div>
            
            <div class="form-group">
              <label for="status">Status *</label>
              <select 
                id="status"
                v-model="status" 
                required
                :disabled="loading"
                autocomplete="off"
              >
                <option value="">Select status</option>
                <option value="New">New</option>
                <option value="Active">Active</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="description">Description</label>
              <textarea 
                id="description"
                v-model="description" 
                placeholder="Enter additional details"
                rows="3"
                :disabled="loading"
                autocomplete="off"
              ></textarea>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="cancel-btn" :disabled="loading">
                Cancel
              </button>
              <button type="submit" class="submit-btn" :disabled="loading">
                Add
              </button>
            </div>
            
            <!-- Only show error message, success will close modal immediately -->
            <div v-if="errorMsg" class="error-message">
              {{ errorMsg }}
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- HTML logic: Popup to show record details -->
    <div v-if="showRecordDetails" class="modal-overlay" @click="closeRecordDetails">
      <div class="modal-content record-details-modal" @click.stop>
        <div class="modal-header">
          <h2>Record Details</h2>
          <button @click="closeRecordDetails" class="close-btn">&times;</button>
        </div>
        
        <div class="record-details-content">
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ selectedRecord.name }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Email:</span>
            <span class="detail-value">{{ selectedRecord.email }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Phone:</span>
            <span class="detail-value">{{ selectedRecord.phone_number }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Organization:</span>
            <span class="detail-value">{{ selectedRecord.organization }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">
              <span :class="['status-badge', getStatusClass(selectedRecord.status)]">
                {{ selectedRecord.status }}
              </span>
            </span>
          </div>
          
          <div class="detail-row full-width" v-if="selectedRecord.description">
            <span class="detail-label">Description:</span>
            <span class="detail-value">{{ selectedRecord.description }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import Draggable from 'vuedraggable'

const API_URL = 'http://127.0.0.1:8000'

const name = ref('')
const email = ref('')
const phone_number = ref('')
const organization = ref('')
const description = ref('')
const status = ref('')
const records = ref([])
const successMsg = ref('')
const errorMsg = ref('') // Add error message ref
const loading = ref(false)
const dragLoading = ref(false)
const currentlyDraggingId = ref(null)
const showAddModal = ref(false)
const showRecordDetails = ref(false)
const selectedRecord = ref({})

const newRecords = computed({
  get() {
    return records.value.filter(r => r.status === 'New')
  },
  set(newRecords) {
    const others = records.value.filter(r => r.status !== 'New')
    records.value = [...others, ...newRecords]
  }
})

const activeRecords = computed({
  get() {
    return records.value.filter(r => r.status === 'Active')
  },
  set(newRecords) {
    const others = records.value.filter(r => r.status !== 'Active')
    records.value = [...others, ...newRecords]
  }
})

const closedRecords = computed({
  get() {
    return records.value.filter(r => r.status === 'Closed')
  },
  set(newRecords) {
    const others = records.value.filter(r => r.status !== 'Closed')
    records.value = [...others, ...newRecords]
  }
})

const checkHorizontalScroll = () => {
  nextTick(() => {
    const container = document.querySelector('.container')
    const body = document.body
    if (container) {
      const containerWidth = container.scrollWidth
      const viewportWidth = window.innerWidth
      if (containerWidth > viewportWidth) {
        body.style.overflowX = 'auto'
        body.style.minWidth = containerWidth + 'px'
      } else {
        body.style.overflowX = 'hidden'
        body.style.minWidth = '100vw'
      }
    }
  })
}

const fetchRecords = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}
    const { data } = await axios.get(`${API_URL}/crm`, { headers })
    records.value = data
    checkHorizontalScroll()
  } catch (err) {
    console.error('Error fetching records:', err)
  }
}

const addRecord = async () => {
  if (!name.value || !status.value) return
  
  loading.value = true
  errorMsg.value = '' // Clear any previous errors
  
  try {
    const token = localStorage.getItem('access_token')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}
    await axios.post(`${API_URL}/crm`, {
      user_id: 1,
      name: name.value,
      email: email.value,
      phone_number: phone_number.value,
      organization: organization.value,
      description: description.value,
      status: status.value
    }, { headers })
    
    // Refresh records
    await fetchRecords()
    
    // Clear form
    name.value = ''
    email.value = ''
    phone_number.value = ''
    organization.value = ''
    description.value = ''
    status.value = ''
    
    // Close modal immediately on success
    showAddModal.value = false
    
  } catch (err) {
    console.error('Error adding record:', err)
    errorMsg.value = 'Failed to add record. Please try again.'
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  if (loading.value) return // Prevent closing while loading
  
  showAddModal.value = false
  successMsg.value = ''
  errorMsg.value = ''
}

const openRecordDetails = (record) => {
  selectedRecord.value = { ...record }
  showRecordDetails.value = true
}

const closeRecordDetails = () => {
  showRecordDetails.value = false
  selectedRecord.value = {}
}

const getStatusClass = (status) => {
  switch (status) {
    case 'New': return 'new-status'
    case 'Active': return 'active-status'
    case 'Closed': return 'closed-status'
    default: return ''
  }
}

const onDrop = async (newStatus, evt) => {
  if (evt.added) {
    const record = evt.added.element
    const oldStatus = record.status
    if (oldStatus === newStatus) return

    dragLoading.value = true
    currentlyDraggingId.value = record.id

    try {
      const token = localStorage.getItem('access_token')
      const headers = token ? { Authorization: `Bearer ${token}` } : {}
      
      await axios.put(`${API_URL}/crm/${record.id}`, {
        ...record,
        status: newStatus
      }, { headers })
      
      const idx = records.value.findIndex(r => r.id === record.id)
      if (idx !== -1) {
        records.value[idx].status = newStatus
      }
      checkHorizontalScroll()
    } catch (err) {
      console.error('Error updating record status:', err)
      await fetchRecords()
    } finally {
      dragLoading.value = false
      currentlyDraggingId.value = null
    }
  }
}

onMounted(() => {
  fetchRecords()
  checkHorizontalScroll()
  window.addEventListener('resize', checkHorizontalScroll)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkHorizontalScroll)
})
</script>

<style>
/* Base Styles */
* {
  margin: 0;
  padding: 0;
}

/* Background */
body {
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
  background-attachment: fixed;
  background-size: 100vw 100vh;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #ffffff;
  overflow-y: auto;
}

body::-webkit-scrollbar {
  height: 8px;
}

body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 4px;
}

body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.6);
}

/* Firefox scrollbar styling for body */
body {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.4) rgba(255, 255, 255, 0.1);
}

/* Action Section */
.action-section {
  margin-top: 20px;
  padding: 20px 0;
}

.action-container {
  display: flex;
  justify-content: flex-start;
  width: max-content;
  min-width: 100%;
  padding: 0 20px;
}

.add-record-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
  backdrop-filter: blur(10px);
  position: static; /* Remove fixed positioning */
  transform: none; /* Remove fixed positioning transforms */
}

.add-record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, #7c3aed, #a855f7);
}

.add-record-btn:active {
  transform: translateY(0);
}

.add-record-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: bold;
  line-height: 1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .action-section {
    margin-top: 20px;
    padding: 15px 0;
  }
  
  .action-container {
    padding: 0 10px;
  }
  
  .add-record-btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideInUp 0.3s ease-out;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f8fafc;
  background: linear-gradient(135deg, #f8fafc, #cbd5e1);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Add modal loading overlay styles */
.modal-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 20px;
  color: #e2e8f0;
  font-weight: 500;
  gap: 16px;
}

.modal-loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.modal-content-inner {
  transition: filter 0.3s ease;
}

.modal-content-inner.blurred {
  filter: blur(2px);
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
}

/* Form Styles */
.record-form {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #f8fafc;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6366f1;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #94a3b8;
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group select {
  cursor: pointer;
}

.form-group select option {
  background: #1e293b;
  color: #f8fafc;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.cancel-btn,
.submit-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.submit-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Success Message */
.success-message {
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 12px;
  color: #6ee7b7;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  animation: slideInUp 0.3s ease-out;
}

/* Error message */
.error-message {
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  color: #fca5a5;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  animation: slideInUp 0.3s ease-out;
}

/* Header Styles */
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  padding: 15px 0;
  background: rgba(10, 10, 10, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
}

.app-title {
  margin-left: 20px;
  font-size: 1.3rem;
  font-weight: 600;
  color: #f8fafc;
  background: linear-gradient(135deg, #f8fafc, #cbd5e1);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Container */
.container {
  width: max-content;
  min-width: 100vw;
  margin: 0;
  position: relative;
  padding: 0;
}

/* Kanban Board */
.kanban-board {
  margin-top: 20px;
  width: max-content;
  min-width: 100vw;
}

.board-header {
  text-align: center;
  margin-bottom: 0px;
}

.board-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0px;
  background: linear-gradient(135deg, #f8fafc, #cbd5e1);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.record-count {
  color: #94a3b8;
  font-size: 1.1rem;
}

/* Container of All Kanban */
.columns-container {
  display: flex;
  flex-wrap: nowrap;
  gap: 20px;
  overflow: visible;
  padding: 10px;
  width: max-content;
  min-width: 1000px;
}

/* Individual Kanban Boards */
.kanban-column {
  position: relative;
  padding: 12px;
  width: 320px;
  min-width: 320px;
  max-width: 320px;
  flex-shrink: 0;
  flex-grow: 0;
  min-height: 500px;
  border-radius: 0px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

@media (min-width: 1200px) {
  .kanban-column {
    width: 380px;
    min-width: 380px;
  }
  
  .columns-container {
    gap: 30px;
  }
}

@media (max-width: 768px) {
  .kanban-column {
    width: 280px;
    min-width: 280px;
    padding: 10px;
  }
  
  .columns-container {
    gap: 15px;
    padding: 5px;
  }
  
  .add-record-btn {
    top: 70px;
    left: 10px;
    padding: 10px 16px;
    font-size: 0.85rem;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .record-form {
    padding: 20px;
  }
}

.new-column {
  border-top: 3px solid #f6c43b;
}

.active-column {
  border-top: 3px solid #3b82f6;
}

.closed-column {
  border-top: 3px solid #10b981;
}

.column-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.column-icon {
  font-size: 1.5rem;
  padding: 10px;
}

.column-header h3 {
  flex: 1;
  font-size: 1.3rem;
  font-weight: 600;
  color: #f8fafc;
}

.record-counter {
  font-size: 0.9rem;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  backdrop-filter: blur(10px);
}

.drag-area {
  min-height: 200px;
  border-radius: 16px;
  position: relative;
  will-change: contents;
}

/* Record Card */
.record-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  padding: 20px;
  margin-bottom: 16px;
  border-radius: 16px;
  cursor: move;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  will-change: transform;
}

.record-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity 0.3s ease;
  background: linear-gradient(90deg, transparent, #6366f1, transparent);
}

.record-card:hover .card-glow {
  opacity: 1;
}

.closed-card .card-glow {
  background: linear-gradient(90deg, transparent, #10b981, transparent);
}

.record-content {
  flex: 1;
}

.record-name {
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 6px;
  color: #f8fafc;
  line-height: 1.4;
}

.record-phone {
  font-size: 0.95rem;
  margin-bottom: 10px;
  color: #94a3b8;
}

.record-status {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 20px;
}

.new-status {
  color: #fce21b;
  background: rgba(251, 238, 180, 0.226);
  border: 1px solid rgba(218, 255, 148, 0.3);
}

.active-status {
  color: #93c5fd;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.closed-status {
  color: #6ee7b7;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.drag-handle {
  color: #64748b;
  font-size: 1.2rem;
  opacity: 0.5;
  cursor: grab;
  transition: opacity 0.3s ease;
}

.record-card:hover .drag-handle {
  opacity: 1;
}

.drag-handle:active {
  cursor: grabbing;
}

/* Drag States */
.ghost-card {
  opacity: 0.5;
  transform: rotate(5deg);
}

.chosen-card {
  transform: scale(1.05);
  z-index: 999;
}

.drag-card {
  transform: rotate(10deg);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5) !important;
}

/* Empty States */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.1rem;
  font-style: italic;
}

/* Animations */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Transitions */
.success-fade-enter-active, .success-fade-leave-active,
.error-fade-enter-active, .error-fade-leave-active {
  transition: all 0.5s ease;
}

.success-fade-enter-from, .success-fade-leave-to,
.error-fade-enter-from, .error-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Drag Loading Styles */
.drag-loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.drag-loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.global-loading-indicator {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #e2e8f0;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  animation: slideInUp 0.3s ease-out;
}

.global-loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Disable interactions when loading */
.drag-area.disabled {
  opacity: 0.7;
  pointer-events: none;
}

/* Record Details Modal Styles */
.record-details-modal {
  max-width: 600px;
}

.record-details-content {
  padding: 25px 30px;
}

.detail-row {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.detail-row.full-width {
  flex-direction: column;
}

.detail-label {
  font-weight: 600;
  color: #e2e8f0;
  min-width: 120px;
  margin-right: 15px;
  flex-shrink: 0;
}

.detail-value {
  color: #f8fafc;
  flex: 1;
  word-break: break-word;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 20px;
}

.detail-actions {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
}

/* Ensure drag handle is still functional */
.drag-handle {
  cursor: grab;
  z-index: 2; /* Ensure it's above the clickable area */
}

.record-card {
  cursor: pointer;
  position: relative;
}

/* Make sure the entire card is clickable except the drag handle */
.record-card > *:not(.drag-handle) {
  pointer-events: none;
}

.record-card .drag-handle {
  pointer-events: auto;
}
</style>