<template>
  <div class="container">
    <!-- Header with gradient background -->
    <header class="header">
      <div class="header-content">
        <h1 class="title">
          <span class="icon">📚</span>
          <span class="text">Reading Tracker</span>
        </h1>
        <div class="subtitle">Organize your literary journey</div>
      </div>
      <div class="header-decoration"></div>
    </header>

    <!-- Add Book Section -->
    <section class="add-book">
      <div class="form-header">
        <h2>Add New Book</h2>
        <div class="form-decoration"></div>
      </div>
      
      <div class="form-grid">
        <div class="input-group">
          <label>Title</label>
          <input 
            v-model="title" 
            placeholder="Enter book title..." 
            class="modern-input"
          />
        </div>
        
        <div class="input-group">
          <label>Author</label>
          <input 
            v-model="author" 
            placeholder="Enter author name..." 
            class="modern-input"
          />
        </div>
        
        <div class="input-group">
          <label>Status</label>
          <select v-model="status" class="modern-select">
            <option value="">Choose status</option>
            <option value="Reading">📖 Currently Reading</option>
            <option value="Completed">✅ Completed</option>
          </select>
        </div>
        
        <div class="button-group">
          <button 
            :disabled="loading || !title || !author || !status" 
            @click="addBook"
            class="add-button"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else class="button-icon">+</span>
            {{ loading ? 'Adding...' : 'Add Book' }}
          </button>
          
          <transition name="success-fade">
            <div v-if="successMsg" class="success-message">
              <span class="success-icon">✨</span>
              {{ successMsg }}
            </div>
          </transition>
        </div>
      </div>
    </section>

    <!-- Kanban Board -->
    <section class="kanban-board">
      <div class="board-header">
        <h2>Your Library</h2>
        <div class="book-count">{{ books.length }} books total</div>
      </div>
      
      <div class="columns-container">
        <div class="kanban-column reading-column">
          <div class="column-header">
            <div class="column-icon">📖</div>
            <h3>Currently Reading</h3>
            <div class="book-counter">{{ readingBooks.length }}</div>
          </div>
          
          <div class="column-content">
            <Draggable
              :list="readingBooks"
              :group="{ name: 'books', pull: true, put: true }"
              item-key="id"
              :animation="300"
              @change="onDrop('Reading', $event)"
              class="drag-area"
              ghost-class="ghost-card"
              chosen-class="chosen-card"
              drag-class="drag-card"
            >
              <template #item="{ element }">
                <div class="book-card" :key="element.id">
                  <div class="card-glow"></div>
                  <div class="book-content">
                    <div class="book-title">{{ element.title }}</div>
                    <div class="book-author">{{ element.author }}</div>
                    <div class="book-status reading-status">Currently Reading</div>
                  </div>
                  <div class="drag-handle">⋮⋮</div>
                </div>
              </template>
            </Draggable>
            
            <!-- Fixed invisible book at bottom -->
            <div class="invisible-book-placeholder"></div>
            
            <div v-if="readingBooks.length === 0" class="empty-state">
              <div class="empty-icon">📚</div>
              <p>Start your reading journey</p>
            </div>
          </div>
        </div>

        <div class="kanban-column completed-column">
          <div class="column-header">
            <div class="column-icon">✅</div>
            <h3>Completed</h3>
            <div class="book-counter">{{ completedBooks.length }}</div>
          </div>
          
          <div class="column-content">
            <Draggable
              :list="completedBooks"
              :group="{ name: 'books', pull: true, put: true }"
              item-key="id"
              :animation="300"
              @change="onDrop('Completed', $event)"
              class="drag-area"
              ghost-class="ghost-card"
              chosen-class="chosen-card"
              drag-class="drag-card"
            >
              <template #item="{ element }">
                <div class="book-card completed-card" :key="element.id">
                  <div class="card-glow"></div>
                  <div class="book-content">
                    <div class="book-title">{{ element.title }}</div>
                    <div class="book-author">{{ element.author }}</div>
                    <div class="book-status completed-status">Completed</div>
                  </div>
                  <div class="drag-handle">⋮⋮</div>
                </div>
              </template>
            </Draggable>
            
            <!-- Fixed invisible book at bottom -->
            <div class="invisible-book-placeholder"></div>
            
            <div v-if="completedBooks.length === 0" class="empty-state">
              <div class="empty-icon">🏆</div>
              <p>Your achievements will appear here</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Draggable from 'vuedraggable'

const API_URL = 'http://127.0.0.1:8000'

const title = ref('')
const author = ref('')
const status = ref('')
const books = ref([])
const successMsg = ref('')
const loading = ref(false)

// Computed properties to filter books by status
const readingBooks = computed({
  get() {
    return books.value.filter(book => book.status === 'Reading')
  },
  set(newBooks) {
    const otherBooks = books.value.filter(book => book.status !== 'Reading')
    books.value = [...otherBooks, ...newBooks]
  }
})

const completedBooks = computed({
  get() {
    return books.value.filter(book => book.status === 'Completed')
  },
  set(newBooks) {
    const otherBooks = books.value.filter(book => book.status !== 'Completed')
    books.value = [...otherBooks, ...newBooks]
  }
})

const fetchBooks = async () => {
  try {
    const { data } = await axios.get(`${API_URL}/books`)
    books.value = data
  } catch (err) {
    console.error('Error fetching books:', err)
  }
}

const addBook = async () => {
  if (!title.value || !author.value || !status.value) return
  loading.value = true
  try {
    await axios.post(`${API_URL}/books`, {
      title: title.value,
      author: author.value,
      status: status.value
    })
    successMsg.value = 'Book added successfully!'
    title.value = ''
    author.value = ''
    status.value = ''
    await fetchBooks()
    setTimeout(() => (successMsg.value = ''), 3000)
  } catch (err) {
    console.error('Error adding book:', err)
  } finally {
    loading.value = false
  }
}

const onDrop = async (newStatus, evt) => {
  if (evt.added) {
    const book = evt.added.element
    const oldStatus = book.status
    
    if (oldStatus === newStatus) return

    try {
      await axios.put(`${API_URL}/books/${book.id}`, {
        ...book,
        status: newStatus
      })
      
      const bookIndex = books.value.findIndex(b => b.id === book.id)
      if (bookIndex !== -1) {
        books.value[bookIndex].status = newStatus
      }
      
    } catch (err) {
      console.error('Error updating book status:', err)
      await fetchBooks()
    }
  }
}

onMounted(fetchBooks)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #ffffff;
  overflow-x: hidden;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
}

/* Header Styles */
.header {
  text-align: center;
  margin-bottom: 60px;
  position: relative;
  padding: 40px 0;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #6366f1, #8b5cf6, transparent);
  border-radius: 1px;
}

.header-content {
  position: relative;
  z-index: 1;
}

.title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.title .icon {
  font-size: 0.8em;
  animation: float 3s ease-in-out infinite;
}

.subtitle {
  font-size: 1.2rem;
  color: #94a3b8;
  font-weight: 300;
  letter-spacing: 0.5px;
}

/* Add Book Section */
.add-book {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  margin-bottom: 60px;
  position: relative;
  overflow: hidden;
}

.add-book::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent);
}

.form-header {
  margin-bottom: 30px;
  text-align: center;
}

.form-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #f8fafc;
}

.form-decoration {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  margin: 0 auto;
  border-radius: 1px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 20px;
  align-items: end;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-size: 0.9rem;
  color: #cbd5e1;
  margin-bottom: 8px;
  font-weight: 500;
}

.modern-input, .modern-select {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 16px 20px;
  color: #ffffff;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

.modern-input:focus, .modern-select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.modern-input::placeholder {
  color: #64748b;
}

.modern-select option {
  background: #1e293b;
  color: #ffffff;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.add-button {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  border-radius: 12px;
  padding: 16px 24px;
  color: white;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.add-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.6s;
}

.add-button:hover:not(:disabled)::before {
  left: 100%;
}

.add-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
}

.add-button:disabled {
  background: rgba(100, 116, 139, 0.3);
  cursor: not-allowed;
  transform: none;
}

.button-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.success-message {
  background: linear-gradient(135deg, #10b981, #34d399);
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  animation: slideInUp 0.5s ease-out;
}

/* Kanban Board */
.kanban-board {
  margin-top: 60px;
}

.board-header {
  text-align: center;
  margin-bottom: 40px;
}

.board-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #f8fafc, #cbd5e1);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.book-count {
  color: #94a3b8;
  font-size: 1.1rem;
}

.columns-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

.kanban-column {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 30px;
  min-height: 500px;
  position: relative;
  transition: all 0.3s ease;
}

.reading-column {
  border-top: 3px solid #3b82f6;
}

.completed-column {
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.column-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #f8fafc;
  flex: 1;
}

.book-counter {
  background: rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.drag-area {
  min-height: 200px;
  border-radius: 16px;
  position: relative;
}

.book-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: move;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-card:hover {
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
  background: linear-gradient(90deg, transparent, #6366f1, transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.book-card:hover .card-glow {
  opacity: 1;
}

.completed-card .card-glow {
  background: linear-gradient(90deg, transparent, #10b981, transparent);
}

.book-content {
  flex: 1;
}

.book-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: #f8fafc;
  margin-bottom: 6px;
  line-height: 1.4;
}

.book-author {
  color: #94a3b8;
  font-size: 0.95rem;
  margin-bottom: 10px;
}

.book-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.reading-status {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.completed-status {
  background: rgba(16, 185, 129, 0.2);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.drag-handle {
  color: #64748b;
  font-size: 1.2rem;
  opacity: 0.5;
  transition: opacity 0.3s ease;
  cursor: grab;
}

.book-card:hover .drag-handle {
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
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* Responsive Design */
@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .button-group {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .columns-container {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .container {
    padding: 15px;
  }
  
  .add-book, .kanban-column {
    padding: 20px;
  }
  
  .title {
    flex-direction: column;
    gap: 10px;
  }
  
  .column-header {
    flex-wrap: wrap;
    gap: 10px;
  }
}

/* Performance optimizations */
.book-card {
  will-change: transform;
}

.drag-area {
  will-change: contents;
}
</style>