# Library Management Frontend

A modern React-based frontend for the Library Management gRPC service, built with Vite, Tailwind CSS, and modern React patterns.

## 🚀 Features

- **📚 Books Management**: Add, view, and delete books
- **👥 Members Management**: Add, view, and delete library members
- **📖 Borrowings Management**: Borrow and return books, track lending status
- **🎨 Modern UI**: Beautiful, responsive design with Tailwind CSS
- **⚡ Fast Development**: Built with Vite for lightning-fast development

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons

## 📦 Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

## 🌐 Usage

The frontend provides three main sections:

### Books Tab
- Add new books with title, author, and ISBN
- View all books in a clean table format
- Delete books as needed

### Members Tab
- Add new members with name, email, and phone
- View all members in a table
- Delete members as needed

### Borrowings Tab
- Borrow books by selecting book and member
- View all borrowing records
- Return books with a single click
- Track borrowing status (borrowed/returned)

## 🔧 Development

- **Port**: Runs on `http://localhost:5173` by default
- **Hot Reload**: Changes reflect immediately in the browser
- **Tailwind**: Use Tailwind classes for styling
- **Components**: All components are in `src/App.jsx`

## 📱 Responsive Design

The UI is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices

## 🎨 Customization

- **Colors**: Modify `tailwind.config.js` for custom color schemes
- **Styling**: Update `src/App.css` for custom styles
- **Layout**: Modify the component structure in `src/App.jsx`

## 🔗 Backend Integration

This frontend is designed to work with the gRPC backend service. In a production environment, you would:

1. Replace mock data with actual API calls
2. Add proper error handling
3. Implement authentication
4. Add loading states and optimistic updates

## 📄 License

This project is part of the Library Management System.
