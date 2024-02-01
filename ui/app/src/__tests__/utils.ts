import { screen } from '@testing-library/react';


export function loginForm() {
  const usernameField = screen.getByLabelText(/Username/);
  const passwordField = screen.getByLabelText(/Password/);
  const loginButton = screen.getByRole('button', { name: 'Login' });

  return {
    usernameField,
    passwordField,
    loginButton,
  }
}


export async function fillOutLoginForm(user, form) {
  await user.type(form.usernameField, 'jojo');
  await user.type(form.passwordField, 'password');
}
