"use client";

import CountUp from "react-countup";

export function AnimatedNumber({
  value,
  prefix = "",
  suffix = "",
  decimals = 0
}: {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
}) {
  return (
    <CountUp
      decimals={decimals}
      decimal=","
      duration={1.2}
      end={value}
      prefix={prefix}
      separator="."
      suffix={suffix}
    />
  );
}
