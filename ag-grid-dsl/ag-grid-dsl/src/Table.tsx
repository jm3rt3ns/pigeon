import { AgGridReact } from "ag-grid-react";
import { useEffect, useState } from "react";

const COLUMN_KEYWORD = '# Columns';

interface TableProps {
    definition: any,
}

const generateTableColumnData = (configText: string) => {
    const splitText = configText.split('\r\n');

    const columnIndex = splitText.findIndex(val => val.includes(COLUMN_KEYWORD));

    if (columnIndex === -1) {
        throw new Error(`Invalid markdown file - need to include keyword ${COLUMN_KEYWORD}`)
    }

    const columnText = splitText.filter((val, idx) => idx > columnIndex);

    // process the column info:
    const result = columnText.join(",").split("## ").filter(val => !!val).map(columnInfo => {
        console.log('info', columnInfo);
        const [columnName, fieldName] = columnInfo.split(",");

        return {
            headerName: columnName, field: fieldName
        }
    });

    console.log(result);

    return result;
}

const Table = (props: TableProps) => {
    const { definition } = props;
    const [tableData, setTableData] = useState<any>();

    // TODO: we want to fetch this as well from the backend via the table definition :)
    const [rowData, _] = useState([
        {
            first_name: 'Clark',
            last_name: 'Kent',
            email: 'ilovepunkrock@dailyplanet.com',
            favorite_ice_cream: 'Pistachio'
        }
    ])

    // TODO: we may want to expose the ability to create shims (inject custom code when the definition is insufficient)

    // load the md file from the expected address
    useEffect(() => {
        console.log('def', definition);
        const colDefs = generateTableColumnData(definition);
        setTableData({ colDefs });
    }, [])

    if (!tableData) {
        return <></>;
    }

    return (
        <AgGridReact
            rowData={rowData}
            columnDefs={tableData.colDefs}
        />
    )
};

export default Table;