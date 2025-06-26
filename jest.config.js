module.exports = {
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['js', 'json'],
  transform: {},
  testMatch: [
    '**/tests/**/*.js',
    '**/__tests__/**/*.js'
  ],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  testPathIgnorePatterns: [
    '/node_modules/'
  ]
}; 