import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  id: string;
  email: string;
  fullName: string;
  createdAt: Date;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  resetPassword: (email: string) => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('oxyra_user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        // Convert createdAt string back to Date
        parsedUser.createdAt = new Date(parsedUser.createdAt);
        setUser(parsedUser);
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('oxyra_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Check if user exists in localStorage
    const storedUsers = localStorage.getItem('oxyra_users');
    const users = storedUsers ? JSON.parse(storedUsers) : [];
    
    const foundUser = users.find(
      (u: any) => u.email === email && u.password === password
    );

    if (!foundUser) {
      throw new Error('Email atau password salah');
    }

    const userData: User = {
      id: foundUser.id,
      email: foundUser.email,
      fullName: foundUser.fullName,
      createdAt: new Date(foundUser.createdAt),
    };

    setUser(userData);
    localStorage.setItem('oxyra_user', JSON.stringify(userData));
  };

  const signup = async (
    fullName: string,
    email: string,
    password: string
  ): Promise<void> => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Check if email already exists
    const storedUsers = localStorage.getItem('oxyra_users');
    const users = storedUsers ? JSON.parse(storedUsers) : [];

    const existingUser = users.find((u: any) => u.email === email);
    if (existingUser) {
      throw new Error('Email sudah terdaftar');
    }

    const newUserData = {
      id: Date.now().toString(),
      email,
      fullName,
      password,
      createdAt: new Date().toISOString(),
    };

    // Save to users list
    users.push(newUserData);
    localStorage.setItem('oxyra_users', JSON.stringify(users));

    // Create user session
    const userData: User = {
      id: newUserData.id,
      email: newUserData.email,
      fullName: newUserData.fullName,
      createdAt: new Date(newUserData.createdAt),
    };

    setUser(userData);
    localStorage.setItem('oxyra_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('oxyra_user');
  };

  const resetPassword = async (email: string): Promise<void> => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const storedUsers = localStorage.getItem('oxyra_users');
    const users = storedUsers ? JSON.parse(storedUsers) : [];

    const foundUser = users.find((u: any) => u.email === email);
    if (!foundUser) {
      throw new Error('Email tidak ditemukan');
    }

    // In a real app, this would send an email
    console.log('Password reset email sent to:', email);
  };

  const updateProfile = async (data: Partial<User>): Promise<void> => {
    if (!user) {
      throw new Error('No user logged in');
    }

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    const updatedUser = { ...user, ...data };
    setUser(updatedUser);
    localStorage.setItem('oxyra_user', JSON.stringify(updatedUser));

    // Update in users list
    const storedUsers = localStorage.getItem('oxyra_users');
    if (storedUsers) {
      const users = JSON.parse(storedUsers);
      const userIndex = users.findIndex((u: any) => u.id === user.id);
      if (userIndex !== -1) {
        users[userIndex] = { ...users[userIndex], ...data };
        localStorage.setItem('oxyra_users', JSON.stringify(users));
      }
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    signup,
    logout,
    resetPassword,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
