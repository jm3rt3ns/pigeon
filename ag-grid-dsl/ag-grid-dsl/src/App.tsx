import { useState } from 'react'
import './App.css'

import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component
import Table from './Table';
import tableDefinition from './table_definition.md';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

interface User {
  first_name: string;
  last_name: string;
  email: string;
  favorite_ice_cream: string;
}

function App() {
  return (
    <div style={{ height: '800px', width: '800px' }}>
      <Table definition={tableDefinition} />
    </div>
  )
}

export default App
