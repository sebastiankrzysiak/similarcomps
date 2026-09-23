export type Home = {
  pin: string;
  address: string;
  city: string;
  bldg_sf: number;
  bldg_av: number;
  bldg_psf: number;
  bldg_market_value: number;
};

export type Comp = {
  pin: string;
  address: string;
  bldg_sf: number;
  year_built: number;
  bldg_av: number;
  bldg_psf: number;
  bldg_market_value: number;
  diff_vs_home: number;
};

export type CompsResponse = {
  home: Home;
  comps: Comp[];
  count: number;
  total_comps: number;
  median_psf: number;
};