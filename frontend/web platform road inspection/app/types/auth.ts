export interface LoginRequestDTO {
  username: string
  password: string
  client_id: string
  redirect_uri: string
  code_challenge: string
  state: string
}

export interface LoginResponseDTO {
  access_token?: string
  redirect_to?: string
}