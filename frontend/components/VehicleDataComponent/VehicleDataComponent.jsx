import Code from "@leafygreen-ui/code";
import { useSelector } from "react-redux";
import styles from './VehicleDataComponent.module.css'

const VehicleDataComponent = () => {
    //using redux for car instead of props
    const car= useSelector((state) => state.Result.selectedCar);

  return (
    <div className={styles.CodeCont}>
        <Code language="json" onCopy={() => {}}>
            {JSON.stringify(car, null, 2)}
        </Code>
    </div>
  );
};

export default VehicleDataComponent;