import React from 'react'
import style from '../portfolio.module.css'

function PBlocks({children, bwidth, bheight}) {
  return (
    <div className={style.pblock} style={{width:bwidth, height:bheight}}>
      <div className={style.container}>
      {children}
      </div>
    </div>
  )
}

export default PBlocks