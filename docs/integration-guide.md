# Everly Frontend Integration Guide

## Introduction

This guide provides instructions for integrating frontend applications with the Everly API. Follow these steps to create a seamless user experience with the Everly personal diary and travel journal backend services.

## Getting Started

### Prerequisites

- Node.js 16 or higher
- Package manager (npm, yarn, or pnpm)
- Basic knowledge of HTTP requests and RESTful APIs
- Google OAuth credentials (for authentication)

### Environment Setup

Create an environment configuration file in your frontend project:

```
# .env.development
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

```
# .env.production
REACT_APP_API_URL=https://api.everly.app/api/v1
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

## Authentication Implementation

### Setting Up Google OAuth

1. Install required packages:

```bash
npm install @react-oauth/google jwt-decode
```

2. Initialize the Google OAuth provider in your app:

```jsx
import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
      {/* Your app components */}
    </GoogleOAuthProvider>
  );
}
```

3. Create a login component:

```jsx
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

function LoginButton() {
  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        // Exchange code for token with backend
        const response = await axios.post(
          `${process.env.REACT_APP_API_URL}/auth/google`,
          { code: codeResponse.code }
        );
        
        // Store token
        localStorage.setItem('token', response.data.data.access_token);
        
        // Configure axios defaults
        axios.defaults.headers.common['Authorization'] = 
          `Bearer ${response.data.data.access_token}`;
          
        // Fetch user profile
        const userResponse = await axios.get(`${process.env.REACT_APP_API_URL}/users/me`);
        
        // Store user info in your app state
        // ...
      } catch (error) {
        console.error('Login failed:', error);
      }
    },
    flow: 'auth-code',
  });

  return (
    <button onClick={() => login()}>Sign in with Google</button>
  );
}
```

### Authentication State Management

Create a custom hook to manage authentication state:

```jsx
import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await axios.get(`${process.env.REACT_APP_API_URL}/users/me`);
          setUser(response.data);
        } catch (error) {
          // Token invalid or expired
          localStorage.removeItem('token');
          delete axios.defaults.headers.common['Authorization'];
        }
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, []);
  
  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };
  
  return (
    <AuthContext.Provider value={{ user, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

## API Client Setup

Create an API client utility:

```javascript
// api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 errors
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## Common API Operations

### User Operations

```javascript
// api/users.js
import apiClient from './client';

export const getUserProfile = () => {
  return apiClient.get('/users/me');
};

export const updateUserProfile = (userData) => {
  return apiClient.put('/users/me', userData);
};

export const getUserPreferences = () => {
  return apiClient.get('/users/me/preferences');
};

export const updateUserPreferences = (preferences) => {
  return apiClient.put('/users/me/preferences', preferences);
};
```

### Diary Operations

```javascript
// api/diaries.js
import apiClient from './client';

export const getDiaryEntries = (page = 1, limit = 10) => {
  return apiClient.get(`/diaries?page=${page}&limit=${limit}`);
};

export const getDiaryEntry = (entryId) => {
  return apiClient.get(`/diaries/${entryId}`);
};

export const createDiaryEntry = (entryData) => {
  return apiClient.post('/diaries', entryData);
};

export const updateDiaryEntry = (entryId, entryData) => {
  return apiClient.put(`/diaries/${entryId}`, entryData);
};

export const deleteDiaryEntry = (entryId) => {
  return apiClient.delete(`/diaries/${entryId}`);
};

export const searchDiaryEntries = (searchParams, page = 1, limit = 10) => {
  return apiClient.post(`/diaries/search?page=${page}&limit=${limit}`, searchParams);
};
```

## UI Component Examples

### Diary Entry Form

```jsx
import { useState } from 'react';
import { createDiaryEntry } from '../api/diaries';

function DiaryEntryForm() {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    content_type: 'text',
    tags: []
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim());
    setFormData({ ...formData, tags });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await createDiaryEntry(formData);
      // Handle success
      setFormData({
        title: '',
        content: '',
        content_type: 'text',
        tags: []
      });
    } catch (error) {
      // Handle error
      console.error('Failed to create entry:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="title">Title</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div>
        <label htmlFor="content">Content</label>
        <textarea
          id="content"
          name="content"
          value={formData.content}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div>
        <label htmlFor="tags">Tags (comma-separated)</label>
        <input
          type="text"
          id="tags"
          name="tags"
          value={formData.tags.join(', ')}
          onChange={handleTagsChange}
        />
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save Entry'}
      </button>
    </form>
  );
}
```

### Diary Entries List

```jsx
import { useState, useEffect } from 'react';
import { getDiaryEntries } from '../api/diaries';

function DiaryEntryList() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [limit] = useState(10);
  
  useEffect(() => {
    fetchEntries();
  }, [page]);
  
  const fetchEntries = async () => {
    try {
      setLoading(true);
      const response = await getDiaryEntries(page, limit);
      setEntries(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Failed to fetch entries:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleNextPage = () => {
    if (page * limit < total) {
      setPage(page + 1);
    }
  };
  
  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };
  
  if (loading && entries.length === 0) {
    return <div>Loading...</div>;
  }
  
  return (
    <div>
      <h2>Your Diary Entries</h2>
      
      {entries.length === 0 ? (
        <p>No entries found. Create your first entry!</p>
      ) : (
        <>
          <ul>
            {entries.map(entry => (
              <li key={entry.id}>
                <h3>{entry.title}</h3>
                <p>{entry.content.substring(0, 100)}...</p>
                <div>
                  {entry.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
                <div>
                  <small>Created: {new Date(entry.created_at).toLocaleString()}</small>
                </div>
              </li>
            ))}
          </ul>
          
          <div className="pagination">
            <button 
              onClick={handlePrevPage} 
              disabled={page === 1}
            >
              Previous
            </button>
            <span>Page {page} of {Math.ceil(total / limit)}</span>
            <button 
              onClick={handleNextPage} 
              disabled={page * limit >= total}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
```

## Error Handling

Implement consistent error handling throughout your application:

```javascript
// utils/error-handler.js
export const handleApiError = (error, defaultMessage = 'An error occurred') => {
  if (error.response && error.response.data) {
    const { message } = error.response.data;
    return message || defaultMessage;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return defaultMessage;
};
```

Usage example:

```jsx
import { handleApiError } from '../utils/error-handler';

try {
  await createDiaryEntry(formData);
  // Success handling
} catch (error) {
  const errorMessage = handleApiError(error, 'Failed to create entry');
  // Display error message to user
  setError(errorMessage);
}
```

## File Upload Implementation

For media content such as images:

```jsx
import { useState } from 'react';
import axios from 'axios';
import apiClient from '../api/client';

function ImageUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [imageUrl, setImageUrl] = useState('');
  
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setUploading(true);
      
      // This assumes you have an endpoint for file uploads
      // Note: Implementation will depend on your backend
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          }
        }
      );
      
      setImageUrl(response.data.url);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div>
      <input type="file" onChange={handleFileChange} accept="image/*" />
      
      <button 
        onClick={handleUpload} 
        disabled={!file || uploading}
      >
        Upload
      </button>
      
      {uploading && (
        <div className="progress-bar">
          <div 
            className="progress" 
            style={{ width: `${progress}%` }}
          >
            {progress}%
          </div>
        </div>
      )}
      
      {imageUrl && (
        <div>
          <img src={imageUrl} alt="Uploaded" width="200" />
        </div>
      )}
    </div>
  );
}
```

## Testing the Integration

1. Start the Everly backend locally:

```bash
python run.py --reload
```

2. Configure the frontend environment to point to the local backend:

```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

3. Test the authentication flow using Google OAuth
4. Test CRUD operations for diary entries
5. Verify error handling works as expected

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure the backend has proper CORS configuration
   - Check that your requests include the appropriate headers

2. **Authentication Failures**
   - Verify that tokens are correctly stored and sent with requests
   - Check token expiration and implement refresh logic if needed

3. **API Connection Issues**
   - Confirm the API URL is correctly set in your environment
   - Verify the backend service is running

### Debugging Tips

1. Use browser developer tools to inspect network requests
2. Add request/response logging in your API client
3. Implement a global error boundary in your React application

## Performance Optimization

1. **Implement caching for frequently accessed data**:

```javascript
import { useQuery, QueryClient, QueryClientProvider } from 'react-query';
import { getDiaryEntries } from '../api/diaries';

// In your app setup
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Your app components */}
    </QueryClientProvider>
  );
}

// In your component
function DiaryEntryList() {
  const { data, isLoading, error } = useQuery(
    ['diaryEntries', page, limit], 
    () => getDiaryEntries(page, limit), 
    { staleTime: 5 * 60 * 1000 } // 5 minutes
  );
  
  // Rest of your component
}
```

2. **Implement pagination and infinite scrolling**
3. **Optimize image loading with lazy loading**
4. **Add skeleton loaders for better UX during API calls**

## Conclusion

This integration guide provides the foundation for building a frontend application that connects to the Everly backend. Refer to the API documentation for detailed endpoint information, and explore the example components to accelerate your development process. 