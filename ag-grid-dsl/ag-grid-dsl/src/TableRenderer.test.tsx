import { render, screen } from '@testing-library/react'
import App from './App'
import { expect, test } from 'vitest'

test('loads and displays greeting', async () => {
    render(<App />);

    // Wait for rows to render
    const rows = await screen.findAllByRole("row");

    // Header row + 6 data rows = 7 rows in total
    screen.logTestingPlaygroundURL();
    let headers = screen.getAllByRole('columnheader', {
        name: /first name/i
    })
    expect(headers[0]).toBeDefined();

    screen.logTestingPlaygroundURL();
    headers = screen.getAllByRole('columnheader', {
        name: /last name/i
    })
    expect(headers[0]).toBeDefined();

    screen.logTestingPlaygroundURL();
    headers = screen.getAllByRole('columnheader', {
        name: /email/i
    })
    expect(headers[0]).toBeDefined();

    screen.logTestingPlaygroundURL();
    headers = screen.getAllByRole('columnheader', {
        name: /favorite flavor ice cream/i
    })
    expect(headers[0]).toBeDefined();
})