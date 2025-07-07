import Code from "@leafygreen-ui/code";

const VehicleDataComponent = ({ children }) => {
  return (
    <Code language="json" onCopy={() => {}}>
      {JSON.stringify(children, null, 2)}
    </Code>
  );
};

export default VehicleDataComponent;