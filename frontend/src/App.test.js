import { render, screen } from '@testing-library/react';
import App from './App';

test('renderiza el título de bienvenida', () => {
  render(<App />);
  const titleElement = screen.getByText(/Bienvenido a Voxia/i);
  expect(titleElement).toBeInTheDocument();
});
