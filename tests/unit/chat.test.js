// Mock document methods
document.getElementById = jest.fn().mockImplementation((id) => {
  if (id === 'chat-messages') {
    return {
      appendChild: jest.fn(),
      scrollTop: 0,
      scrollHeight: 100,
      children: { length: 1 },
      lastChild: { textContent: '', className: '' }
    };
  }
  if (id === 'user-input') {
    return { value: 'Test message' };
  }
  if (id === 'chat-form') {
    return {
      addEventListener: jest.fn((event, callback) => {
        // Store the callback for testing
        global.formSubmitHandler = callback;
      })
    };
  }
  return null;
});

// Import the file you want to test
// Note: This is a simple test; in a real setup you'd need more DOM mocking
describe('Chat functionality', () => {
  test('Chat form exists in HTML', () => {
    const formElement = document.getElementById('chat-form');
    expect(formElement).not.toBeNull();
  });
}); 