# Saarthi Backend Project

This project is a backend service for Saarthi. We welcome contributions from the community!

## How to Contribute

Thank you for considering contributing to the Saarthi backend project. Your help is valuable in making this project better. Please follow these guidelines when contributing:

### 1. Setting Up Your Development Environment

To get started, you'll need to set up your local development environment.

*   **Prerequisites:**
    *   Python 3.8+
    *   `pip` (Python package installer)

*   **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/saarthi-backend.git
    cd saarthi-backend
    ```
    *(Note: Replace `https://github.com/your-username/saarthi-backend.git` with the actual repository URL if it's different.)*

*   **Install Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

*   **Database Setup:**
    This project uses Django. You'll need to set up your database.
    ```bash
    python manage.py migrate
    ```
    *(For local development, SQLite is used by default. For other databases, refer to `saarthi_backend/settings.py`.)*

### 2. Making Changes

*   **Branching:**
    Create a new branch for your feature or bug fix. Use a descriptive name, e.g., `feature/add-user-profile` or `fix/login-bug`.
    ```bash
    git checkout -b your-branch-name
    ```

*   **Coding Standards:**
    *   Follow PEP 8 guidelines for Python code.
    *   Write clear, concise, and well-documented code.
    *   Add unit tests for new features or bug fixes.

*   **Running Tests:**
    ```bash
    python manage.py test
    ```

### 3. Submitting Your Changes

*   **Commit Messages:**
    Write clear and concise commit messages. Follow the Conventional Commits specification if possible (e.g., `feat: add user profile endpoint`, `fix: resolve authentication issue`).

*   **Pull Requests:**
    1.  Ensure your branch is up-to-date with the main branch:
        ```bash
        git checkout main
        git pull origin main
        git checkout your-branch-name
        git merge main
        ```
    2.  Push your branch to the remote repository:
        ```bash
        git push origin your-branch-name
        ```
    3.  Open a Pull Request on GitHub.
    4.  Provide a clear description of your changes, the problem they solve, and any relevant context.

### 4. Code of Conduct

Please note that we have a Code of Conduct that all contributors must adhere to. By participating in this project, you agree to abide by its terms.

### 5. Questions and Support

If you have any questions or need assistance, please open an issue on the GitHub repository.

---

**License:**
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
*(Note: Replace MIT License and LICENSE.md if a different license is used.)*
