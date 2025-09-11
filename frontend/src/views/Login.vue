<template>
  <div class="login-container">

    <!-- Main Content -->
    <div class="login-content">
      <!-- Logo/Brand Section -->
      <div class="brand-section">
        <div class="brand-icon">📋</div>
        <h1 class="brand-title">CRM Kanban</h1>
        <p class="brand-subtitle">Streamline your customer relationships</p>
      </div>

      <!-- Login Form -->
      <div class="login-form-container">
        <div class="login-form-wrapper">
          <!-- Loading Overlay -->
          <div v-if="loading" class="form-loading-overlay">
            <div class="form-loading-spinner"></div>
            <span>{{ isLogin ? 'Signing you in...' : 'Creating account...' }}</span>
          </div>

          <div :class="['login-form', { 'form-blurred': loading }]">
            <div class="form-header">
              <h2>{{ isLogin ? 'Welcome' : 'Create Account' }}</h2>
              <p>{{ isLogin ? 'Sign in to access your CRM dashboard' : 'Join us to manage your customer relationships' }}</p>
            </div>

            <form @submit.prevent="isLogin ? handleLogin() : handleRegister()" class="auth-form">
              <div class="input-group">
                <div class="input-wrapper">
                  <input
                    type="email"
                    id="email"
                    v-model="email"
                    placeholder="Email"
                    required
                    :disabled="loading"
                    autocomplete="email"
                  >
                </div>
              </div>

              <div class="input-group">
                <div class="input-wrapper">
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    id="password"
                    v-model="password"
                    placeholder="Password"
                    required
                    :disabled="loading"
                    :autocomplete="isLogin ? 'current-password' : 'new-password'"
                  >
                  <button
                    type="button"
                    class="password-toggle"
                    @click="showPassword = !showPassword"
                    :disabled="loading"
                  >
                    {{ showPassword ? '⚫' : '⚪' }}
                  </button>
                </div>
              </div>

              <div class="form-options" v-if="isLogin">
                <a href="#" class="forgot-password">Forgot password?***</a>
              </div>

              <button type="submit" class="login-btn" :disabled="loading || !isFormValid">
                <span v-if="!loading">{{ isLogin ? 'Sign In' : 'Sign Up' }}</span>
                <div v-else class="btn-loading">
                  <div class="btn-spinner"></div>
                  <span>{{ isLogin ? 'Signing in...' : 'Creating account...' }}</span>
                </div>
              </button>

              <!-- Error Message -->
              <div v-if="errorMessage" class="error-message">
                {{ errorMessage }}
              </div>

              <!-- Success Message -->
              <div v-if="successMessage" class="success-message">
                {{ successMessage }}
              </div>
            </form>

            <div class="form-footer">
              <p v-if="isLogin">
                Don't have an account? 
                <a href="#" @click="toggleMode" class="signup-link">Sign up here</a>
              </p>
              <p v-else>
                Already have an account? 
                <a href="#" @click="toggleMode" class="signup-link">Sign in here</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Form data
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isLogin = ref(true)

const API_BASE_URL = 'http://127.0.0.1:8000'

// Form validation
const isFormValid = computed(() => {
  return email.value.trim() !== '' && password.value.trim() !== '' && password.value.length >= 6
})

// Clear messages when switching modes
const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
  successMessage.value = ''
}

// NEW: Single form submit handler
const handleFormSubmit = () => {
  console.log('Form submitted!') // Debug log
  if (isLogin.value) {
    handleLogin()
  } else {
    handleRegister()
  }
}

const handleLogin = async () => {
  console.log('handleLogin called') // Debug log
  if (!isFormValid.value) {
    errorMessage.value = 'Please fill in all fields with valid data'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    console.log('Attempting login for:', email.value)
    
    const response = await axios.post(`${API_BASE_URL}/login`, {
      email: email.value.trim(),
      password: password.value
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    
    console.log('Login response:', response.data)
    
    if (response.data.access_token) {
      successMessage.value = 'Login successful! Redirecting...'
      
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('userEmail', email.value)

      // Check if there's a redirect query parameter
      const redirect = router.currentRoute.value.query.redirect
      const redirectPath = redirect || '/app'
      
      setTimeout(() => {
        router.push(redirectPath)
      }, 1000)
    } else {
      throw new Error('No access token received')
    }
    
  } catch (error) {
    console.error('Login error:', error)
    
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      errorMessage.value = 'Unable to connect to server. Please check if the backend is running.'
    } else if (error.response?.status === 401) {
      errorMessage.value = 'Invalid email or password'
    } else if (error.response?.status === 422) {
      errorMessage.value = 'Please check your email format and try again'
    } else if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'Login failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  console.log('handleRegister called') // Debug log
  if (!isFormValid.value) {
    errorMessage.value = 'Please fill in all fields. Password must be at least 6 characters.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    console.log('Attempting registration for:', email.value)
    
    const response = await axios.post(`${API_BASE_URL}/register`, {
      email: email.value.trim(),
      password: password.value
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    
    console.log('Registration response:', response.data)
    
    successMessage.value = 'Account created successfully! Please login.'
    
    setTimeout(() => {
      isLogin.value = true
      password.value = ''
      successMessage.value = ''
    }, 2000)
    
  } catch (error) {
    console.error('Registration error:', error)
    
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      errorMessage.value = 'Unable to connect to server. Please check if the backend is running.'
    } else if (error.response?.status === 400) {
      errorMessage.value = 'Email already registered. Please try logging in instead.'
    } else if (error.response?.status === 422) {
      errorMessage.value = 'Please check your email format and ensure password is at least 6 characters'
    } else if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

// In your App.vue or a separate auth service
const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('isLoggedIn')
  localStorage.removeItem('userEmail')
  router.push('/login')
}

// Add this for debugging
console.log('Login.vue component mounted') // Debug log
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

.login-container {
  display: flex;
}

/* Main Content - Updated for responsive layout */
.login-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 40px;
  width: 100%;
  max-width: 1200px;
  z-index: 1;
  padding: 20px;
}

/* Brand Section - Updated for responsive positioning */
.brand-section {
  text-align: center;
  color: rgb(255, 255, 255);
  order: 1;
}

.brand-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

.brand-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #f8fafc, #cbd5e1);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 1rem;
  color: #94a3b8;
  font-weight: 400;
}

/* Login Form - Updated for responsive positioning */
.login-form-container {
  position: relative;
  order: 2;
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0px;
}

.login-form-wrapper {
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 0;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 400px;
  position: relative;
  overflow: hidden;
}

.form-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 24px;
  color: #e2e8f0;
  font-weight: 500;
  gap: 16px;
}

.form-loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.login-form {
  padding: 40px;
  transition: filter 0.3s ease;
}

.login-form.form-blurred {
  filter: blur(2px);
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 8px;
}

.form-header p {
  color: #94a3b8;
  font-size: 0.95rem;
}

/* Form Inputs */
.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 50px 14px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #f8fafc;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.input-wrapper input:focus {
  outline: none;
  border-color: #6366f1;
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.input-wrapper input::placeholder {
  color: #94a3b8;
}

.input-icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.6;
}

.password-toggle {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.password-toggle:hover {
  opacity: 1;
}

/* Form Options */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.checkbox-wrapper input {
  margin-right: 8px;
}

.forgot-password {
  color: #6366f1;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #8b5cf6;
}

/* Login Button */
.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
  margin-bottom: 20px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, #7c3aed, #a855f7);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Messages */
.error-message {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  color: #fca5a5;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  margin-bottom: 15px;
}

.success-message {
  padding: 12px 16px;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 12px;
  color: #6ee7b7;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  margin-bottom: 15px;
}

/* Form Footer */
.form-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.form-footer p {
  color: #94a3b8;
  font-size: 0.9rem;
}

.signup-link {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.signup-link:hover {
  color: #8b5cf6;
}


/* Responsive adjustments for smaller screens */
@media (min-width: 1024px) {
  .login-content {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 60px;
  }
  
  .brand-section {
    text-align: left;
    flex: 1;
    order: 1;
    padding-right: 40px;
  }
  
  .login-form-container {
    flex: 0 0 auto;
    order: 2;
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }
  
  .login-content {
    gap: 30px;
  }
  
  .brand-title {
    font-size: 2.5rem;
  }
  
  .brand-subtitle {
    font-size: 1.1rem;
  }
  
  .login-form {
    padding: 30px 25px;
  }
}

@media (max-width: 480px) {
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-icon {
    font-size: 3rem;
  }
  
  .login-form {
    padding: 25px 20px;
  }
  
  .form-header h2 {
    font-size: 1.5rem;
  }
  
  .floating-shape {
    transform: scale(0.6);
  }
}

/* Animations */
@keyframes float {
  0%, 100% { 
    transform: translateY(0px); 
  }
  50% { 
    transform: translateY(-20px); 
  }
}

@keyframes spin {
  0% { 
    transform: rotate(0deg); 
  }
  100% { 
    transform: rotate(360deg); 
  }
}
</style>