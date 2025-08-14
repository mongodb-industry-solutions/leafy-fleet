import Code from "@leafygreen-ui/code";
import { useSelector } from "react-redux";
import styles from './StaticComponent.module.css'

const StaticComponent = () => {
    //using redux for car instead of props
    const staticCar = useSelector((state) => state.Result.staticSelectedCar); // Static data  

  return (
    <div className={styles.CodeCont}>
        <Code language="json" onCopy={() => {}}>
            {JSON.stringify(staticCar, null, 2)}
        </Code>
    </div>
  );
};

export default StaticComponent;