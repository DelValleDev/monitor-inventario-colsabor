export function Loader({ label = "Sincronizando datos..." }: { label?: string }) {
  return (
    <div className="loader-panel">
      <div className="loader-ring" />
      <div>
        <div className="loader-title">{label}</div>
        <div className="muted">Optimizando inventario en tiempo real.</div>
      </div>
    </div>
  );
}
