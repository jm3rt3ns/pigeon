import "@testing-library/jest-dom";
import { cleanup } from "@testing-library/react";
// Ensure cleanup after each test
afterEach(() => {
 cleanup();
});

// Override the innerText setter to use textContent instead within jsdom based tests
Object.defineProperty(Element.prototype, 'innerText', {
    set(value) {
        this.textContent = value;
    },
});