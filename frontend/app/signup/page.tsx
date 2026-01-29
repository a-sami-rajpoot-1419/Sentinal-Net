/**
 * Sign Up Page
 */

import SignUpForm from '@/components/auth/SignUpForm';

export const metadata = {
  title: 'Sign Up - Sentinel-Net',
  description: 'Create a new Sentinel-Net account',
};

export default function SignUpPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Sentinel-Net</h1>
          <p className="text-gray-600">ML Agent Consensus Engine</p>
        </div>

        <SignUpForm />

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            By creating an account, you agree to our{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
              Terms of Service
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
