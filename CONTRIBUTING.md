# Contributing to Enterprise CX Guardian AI

Thank you for considering contributing to **Enterprise CX Guardian AI**! We welcome bug reports, feature requests, documentation improvements, and pull requests.

---

## 🛠️ Code of Conduct

Maintain a professional, respectful, and inclusive environment for all contributors.

---

## 🚀 How to Contribute

### 1. Reporting Bugs
Before opening an issue, please search existing issues to avoid duplicates. When filing a bug report:
- Include operating system, Node.js version, and Python version details.
- Provide step-by-step reproduction instructions.
- Attach log outputs or stack traces.

### 2. Feature Requests
Open an issue tagged `enhancement` describing:
- The problem your feature solves.
- Proposed implementation details.
- Potential breaking changes.

### 3. Submitting Pull Requests
1. **Fork the Repository**:
   ```bash
   git clone https://github.com/your-username/ai-microservice.git
   cd ai-microservice
   ```
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```
3. **Run Tests & Verify**:
   ```bash
   # Run Python AI Microservice tests
   cd ai-service && pytest

   # Run Node Gateway tests
   cd ../server && npm test
   ```
4. **Commit Changes**: Use clean, descriptive commit messages:
   ```bash
   git commit -m "feat(security): implement sliding-window rate limit headers"
   ```
5. **Push & Open Pull Request**: Push to your fork and submit a PR against the `main` branch.

---

## 📐 Coding Standards

- **Python**: Follow PEP 8 guidelines. Use type hints (`typing`) on all function definitions.
- **Node.js**: Follow ES Module (`import`/`export`) syntax. Use async/await over raw promises.
- **React**: Use functional components with hooks. Prefer TailwindCSS utility classes.

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE).
