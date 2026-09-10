export const useSession = () => {
  const user = useState('current_user', () => null)
  const token = useCookie('access_token')

  const isLoggedIn = computed(() => !!token.value)

  return { user, token, isLoggedIn }
}