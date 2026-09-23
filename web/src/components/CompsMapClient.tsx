"use client";

import dynamic from "next/dynamic";

const CompsMap = dynamic(() => import("./CompsMap"), { ssr: false });

export default CompsMap;