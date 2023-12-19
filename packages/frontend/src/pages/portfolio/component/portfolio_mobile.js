import React from "react";
import style from '../portfolio.module.css';
import Layout from "../../../component/layout";

const Mobile = () => {
  return (
    <Layout>
      <div className={style.portfolio_mobile}>
          To fully experience the design and content of this website mock-up,
          please open it in a laptop or desktop browser for a better view.
      </div>
    </Layout>
  );
};

export default Mobile;
