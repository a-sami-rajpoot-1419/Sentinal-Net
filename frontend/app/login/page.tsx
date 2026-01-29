/**
 * Login Page
 */

import LoginForm from '@/components/auth/LoginForm';

export const metadata = {
  title: 'Login - Sentinel-Net',
  description: 'Sign in to your Sentinel-Net account',
};

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Sentinel-Net</h1>
          <p className="text-gray-600">ML Agent Consensus Engine</p>
        </div>

        <LoginForm />

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            By signing in, you agree to our{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
              Terms of Service
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
