# Skill: nextjs-component

**Name**: nextjs-component  
**Description**: Generates reusable Next.js TypeScript components with Tailwind, shadcn/ui, forms, and axios Bearer token API calls

## Purpose
This skill generates reusable Next.js components using TypeScript, Tailwind CSS, shadcn/ui components, and axios for API calls with Bearer token authentication. The components follow modern best practices for state management, error handling, and responsive design.

## Allowed Tools
- code_write
- file_edit

## Implementation Instructions

### 1. Component Structure
Create components in the `src/components` directory with the following structure:
```
components/
├── ui/
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   └── ...
├── TaskCard.tsx
├── TaskForm.tsx
├── AuthButton.tsx
└── ...
```

### 2. Axios Instance with Interceptors
```typescript
// src/lib/axios-instance.ts
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
});

// Add Bearer token to requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('better-auth-token'); // Or however you store the token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle token expiration (e.g., redirect to login)
      localStorage.removeItem('better-auth-token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

### 3. Example Component: TaskCard
```tsx
// src/components/TaskCard.tsx
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Task } from '@/types/task';
import { Trash2, Edit } from 'lucide-react';
import { useState } from 'react';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => void;
  onToggleComplete: (taskId: number) => void;
}

export function TaskCard({ 
  task, 
  onEdit, 
  onDelete, 
  onToggleComplete 
}: TaskCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleComplete = async () => {
    setIsLoading(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className={`transition-all duration-200 ${task.completed ? 'opacity-70' : ''}`}>
      <CardContent className="p-4 pt-6">
        <div className="flex items-start space-x-3">
          <Checkbox
            checked={task.completed}
            onCheckedChange={handleToggleComplete}
            disabled={isLoading}
            className="mt-1"
          />
          <div className="flex-1 min-w-0">
            <h3 className={`font-semibold truncate ${task.completed ? 'line-through' : ''}`}>
              {task.title}
            </h3>
            {task.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {task.description}
              </p>
            )}
            <div className="flex items-center gap-2 mt-2">
              <Badge variant={task.priority === 'high' ? 'destructive' : task.priority === 'medium' ? 'default' : 'secondary'}>
                {task.priority}
              </Badge>
              <Badge variant={task.status === 'completed' ? 'secondary' : 'outline'}>
                {task.status}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-end space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(task)}
          disabled={isLoading}
        >
          <Edit className="w-4 h-4 mr-1" />
          Edit
        </Button>
        <Button
          variant="destructive"
          size="sm"
          onClick={handleDelete}
          disabled={isLoading}
        >
          <Trash2 className="w-4 h-4 mr-1" />
          Delete
        </Button>
      </CardFooter>
    </Card>
  );
}
```

### 4. Example Component: TaskForm
```tsx
// src/components/TaskForm.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Task } from '@/types/task';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high']),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function TaskForm({ 
  task, 
  onSubmit, 
  onCancel, 
  isLoading = false 
}: TaskFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    reset
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: task?.title || '',
      description: task?.description || '',
      priority: task?.priority || 'medium',
    }
  });

  const handleFormSubmit = (data: TaskFormData) => {
    onSubmit(data);
    reset(); // Reset form after submission
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{task ? 'Edit Task' : 'Create Task'}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              {...register('title')}
              placeholder="Task title"
            />
            {errors.title && (
              <p className="text-sm text-destructive">{errors.title.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              {...register('description')}
              placeholder="Task description"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select
              value={task?.priority || 'medium'}
              onValueChange={(value) => setValue('priority', value as 'low' | 'medium' | 'high')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Saving...' : task ? 'Update Task' : 'Create Task'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

### 5. Example Component: AuthButton
```tsx
// src/components/AuthButton.tsx
import { Button } from '@/components/ui/button';
import { signIn, signOut, useUser } from '@clerk/nextjs';
import { LogIn, LogOut } from 'lucide-react';

interface AuthButtonProps {
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export function AuthButton({ variant = 'default', size = 'default' }: AuthButtonProps) {
  const { isSignedIn } = useUser();

  return (
    <Button
      variant={variant}
      size={size}
      onClick={() => {
        if (isSignedIn) {
          signOut();
        } else {
          signIn();
        }
      }}
    >
      {isSignedIn ? (
        <>
          <LogOut className="w-4 h-4 mr-2" />
          Sign Out
        </>
      ) : (
        <>
          <LogIn className="w-4 h-4 mr-2" />
          Sign In
        </>
      )}
    </Button>
  );
}
```

### 6. Theme Provider for Dark/Light Mode
```tsx
// src/providers/ThemeProvider.tsx
'use client';

import * as React from 'react';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { type ThemeProviderProps } from 'next-themes/dist/types';

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

### 7. Responsive Design Guidelines
- Use Tailwind's responsive prefixes (sm:, md:, lg:, xl:, 2xl:)
- Implement mobile-first design approach
- Ensure touch targets are at least 44px for mobile devices
- Use appropriate padding and spacing for different screen sizes

### 8. Loading and Error States
```tsx
// Example of handling loading and error states
import { useState, useEffect } from 'react';
import { toast } from 'sonner'; // or your preferred toast library

export function useApiCall<T>(apiFunction: () => Promise<T>, deps: React.DependencyList = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiFunction();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
        toast.error('Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, deps);

  return { data, loading, error };
}
```

## Key Features
- Uses TypeScript for type safety
- Implements Next.js App Router structure
- Integrates Tailwind CSS for styling
- Uses shadcn/ui components for consistent UI
- Implements axios with interceptors for API calls
- Attaches Bearer token from Better Auth to requests
- Handles loading and error states
- Responsive design with mobile-first approach
- Dark/light mode support
- Reusable component architecture

## Best Practices
- Use TypeScript interfaces for props and data structures
- Implement proper error boundaries
- Use React hooks for state management
- Follow accessibility guidelines (ARIA attributes, keyboard navigation)
- Optimize images and assets
- Implement proper loading states
- Use Sonner or similar for toast notifications
- Follow Next.js best practices for performance