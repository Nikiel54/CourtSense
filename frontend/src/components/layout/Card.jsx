
// Re-usbale wrapper for a card ui
export default function Card({ children, display }) {
  return (
    <div className="card-wrapper">
      <div className={`card ${display}`}>
        {children}
      </div>
    </div>
  );
}