// For CSS/Sass Modules (e.g., import styles from './styles.module.scss')
declare module '*.module.scss' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.module.sass' {
  const classes: { [key: string]: string };
  export default classes;
}

// For global CSS side-effect imports
declare module '*.css';

// For CSS Modules (if you use them)
declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

// For Global/Side-Effect Stylesheets (e.g., import './styles.scss')
declare module '*.scss';
declare module '*.sass';
