'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, logout, User } from '@/lib/auth'
import { 
  Briefcase, 
  Sparkles, 
  MessageSquare, 
  Bookmark, 
  User as UserIcon, 
  Settings,
  LogOut,
  CheckCircle2,
  Shield
} from 'lucide-react'
import LoadingPage from '@/app/components/LoadingPage'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/auth/login')
        return
      }
      setUser(currentUser)
    } catch (error) {
      router.push('/auth/login')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingPage />
  }

  if (!user) {
    return null
  }

  const menuItems = [
    {
      href: '/jobs',
      icon: Briefcase,
      title: 'Browse Jobs',
      description: 'Search and browse available job listings',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600'
    },
    {
      href: '/recommendations',
      icon: Sparkles,
      title: 'Recommendations',
      description: 'Get AI-powered job recommendations',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600'
    },
    {
      href: '/chat',
      icon: MessageSquare,
      title: 'Career Advisor',
      description: 'Chat with AI career advisor',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600'
    },
    {
      href: '/saved',
      icon: Bookmark,
      title: 'Saved Jobs',
      description: 'View your saved job listings',
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600'
    },
    {
      href: '/profile/edit',
      icon: UserIcon,
      title: 'Edit Profile',
      description: 'Update your profile information and preferences',
      color: 'from-indigo-500 to-indigo-600',
      bgColor: 'bg-indigo-50',
      iconColor: 'text-indigo-600'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Dashboard
              </h1>
              {user.onboarding_completed && (
                <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Profile Complete
                </p>
              )}
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user.full_name || user.email}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {!user.onboarding_completed && (
          <div className="mb-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-6 rounded-xl shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Complete Your Profile
                </h2>
                <p className="text-blue-100">Complete your profile to get personalized job recommendations</p>
              </div>
              <Link
                href="/onboarding"
                className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-medium transition shadow-md"
              >
                Get Started
              </Link>
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className="group bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100"
              >
                <div className={`w-12 h-12 ${item.bgColor} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className={`w-6 h-6 ${item.iconColor}`} />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition">
                  {item.title}
                </h2>
                <p className="text-gray-600 text-sm">{item.description}</p>
              </Link>
            )
          })}

          {user.is_admin && (
            <Link
              href="/admin"
              className="group bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
            >
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-semibold mb-2">Admin Dashboard</h2>
              <p className="text-purple-100 text-sm">Manage jobs, users, and system settings</p>
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}



