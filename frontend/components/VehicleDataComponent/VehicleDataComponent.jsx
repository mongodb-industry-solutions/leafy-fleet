import Code from "@leafygreen-ui/code";
import { useSelector } from "react-redux";
const VehicleDataComponent = ({  }) => {
    const car= useSelector((state) => state.Result.selectedCar);
  return (
    <Code language="json" onCopy={() => {}}>
      {JSON.stringify(car, null, 2)}
    </Code>
  );
};

export default VehicleDataComponent;