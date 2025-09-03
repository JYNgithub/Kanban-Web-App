<template>
  <div class="container">
    <h1>📚 Books Kanban</h1>

    <!-- Add Book Section -->
    <section class="add-book">
      <h2>Add a Book</h2>
      <input v-model="title" placeholder="Title" />
      <input v-model="author" placeholder="Author" />
      <select v-model="status">
        <option value="">Select Status</option>
        <option value="Reading">Reading</option>
        <option value="Completed">Completed</option>
      </select>
      <button :disabled="loading" @click="addBook">Add Book</button>
      <p v-if="successMsg" class="success">{{ successMsg }}</p>
    </section>

    <!-- Kanban Board -->
    <section class="kanban-board">
      <div class="kanban-column">
        <h3>📖 Reading</h3>
        <div class="book-card" v-for="book in readingBooks" :key="book.id">
          <div class="book-title">{{ book.title }}</div>
          <div class="book-author">by {{ book.author }}</div>
        </div>
      </div>

      <div class="kanban-column">
        <h3>✅ Completed</h3>
        <div class="book-card" v-for="book in completedBooks" :key="book.id">
          <div class="book-title">{{ book.title }}</div>
          <div class="book-author">by {{ book.author }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

const title = ref('')
const author = ref('')
const status = ref('')
const books = ref([])
const successMsg = ref('')
const loading = ref(false)

const readingBooks = computed(() => 
  books.value.filter(book => book.status === 'Reading')
)

const completedBooks = computed(() => 
  books.value.filter(book => book.status === 'Completed')
)

const fetchBooks = async () => {
  try {
    const response = await axios.get(`${API_URL}/books`)
    books.value = response.data
  } catch (err) {
    console.error(err)
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
    successMsg.value = 'Book added!'
    title.value = ''
    author.value = ''
    status.value = ''
    fetchBooks()
    setTimeout(() => successMsg.value = '', 3000)
  } catch (err) {
    console.error(err)
  }
  loading.value = false
}

onMounted(fetchBooks)
</script>

<style>
.container {
  max-width: 800px;
  margin: 40px auto;
  font-family: sans-serif;
  padding: 20px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.add-book {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  border: 1px solid #e9ecef;
}

.add-book h2 {
  margin-top: 0;
  color: #495057;
}

input, select {
  display: block;
  margin: 10px 0;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.success {
  color: #28a745;
  margin-top: 10px;
  font-weight: bold;
}

.kanban-board {
  display: flex;
  gap: 20px;
}

.kanban-column {
  flex: 1;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e9ecef;
}

.kanban-column h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #495057;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 2px solid #dee2e6;
}

.book-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.book-title {
  font-weight: bold;
  color: #212529;
  margin-bottom: 5px;
}

.book-author {
  color: #6c757d;
  font-size: 14px;
}

/* Responsive design */
@media (max-width: 600px) {
  .kanban-board {
    flex-direction: column;
  }
  
  .container {
    margin: 20px;
    padding: 15px;
  }
}
</style>