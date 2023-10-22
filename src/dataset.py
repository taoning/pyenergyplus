import os

datadir = os.path.join(os.path.dirname(__file__), "data")
modeldir = os.path.join(datadir, "model")
weatherdir = os.path.join(datadir, "weather")

ref_models = {
    "full_service_restaurant": os.path.join(modeldir, "RefBldgFullServiceRestaurantNew2004_Chicago.idf"),
    "hospital": os.path.join(modeldir, "RefBldgHospitalNew2004_Chicago.idf"),
    "large_hotel": os.path.join(modeldir, "RefBldgLargeHotelNew2004_Chicago.idf"),
    "large_office": os.path.join(modeldir, "RefBldgLargeOfficeNew2004_Chicago.idf"),
    "medium_office": os.path.join(modeldir, "RefBldgMediumOfficeNew2004_Chicago.idf"),
    "midrise_apartment": os.path.join(modeldir, "RefBldgMidriseApartmentNew2004_Chicago.idf"),
    "outpatient": os.path.join(modeldir, "RefBldgOutPatientNew2004_Chicago.idf"),
    "primary_school": os.path.join(modeldir, "RefBldgPrimarySchoolNew2004_Chicago.idf"),
    "quick_service_restaurant": os.path.join(modeldir, "RefBldgQuickServiceRestaurantNew2004_Chicago.idf"),
    "secondary_school": os.path.join(modeldir, "RefBldgSecondarySchoolNew2004_Chicago.idf"),
    "small_hotel": os.path.join(modeldir, "RefBldgSmallHotelNew2004_Chicago.idf"),
    "small_office": os.path.join(modeldir, "RefBldgSmallOfficeNew2004_Chicago.idf"),
    "standalone_retail": os.path.join(modeldir, "RefBldgStand-aloneRetailNew2004_Chicago.idf"),
    "strip_mall": os.path.join(modeldir, "RefBldgStripMallNew2004_Chicago.idf"),
    "supermarket": os.path.join(modeldir, "RefBldgSuperMarketNew2004_Chicago.idf"),
    "warehouse": os.path.join(modeldir, "RefBldgWarehouseNew2004_Chicago.idf"),
}


ashrae_models = {
    "apartment_high_rise": os.path.join(modeldir, "ASHRAE901_ApartmentHighRise_STD2019_Denver.idf"),
    "apartment_mid_rise": os.path.join(modeldir, "ASHRAE901_ApartmentMidRise_STD2019_Denver.idf"),
    "hospital": os.path.join(modeldir, "ASHRAE901_Hospital_STD2019_Denver.idf"),
    "hotel_large": os.path.join(modeldir, "ASHRAE901_HotelLarge_STD2019_Denver.idf"),
    "hotel_small": os.path.join(modeldir, "ASHRAE901_HotelSmall_STD2019_Denver.idf"),
    "office_large": os.path.join(modeldir, "ASHRAE901_OfficeLarge_STD2019_Denver.idf"),
    "office_medium": os.path.join(modeldir, "ASHRAE901_OfficeMedium_STD2019_Denver.idf"),
    "office_small": os.path.join(modeldir, "ASHRAE901_OfficeSmall_STD2019_Denver.idf"),
    "outpatient": os.path.join(modeldir, "ASHRAE901_OutPatientHealthCare_STD2019_Denver.idf"),
    "restaurant_fast_food": os.path.join(modeldir, "ASHRAE901_RestaurantFastFood_STD2019_Denver.idf"),
    "restaurant_sit_down": os.path.join(modeldir, "ASHRAE901_RestaurantSitDown_STD2019_Denver.idf"),
    "retail_standalone": os.path.join(modeldir, "ASHRAE901_RetailStandalone_STD2019_Denver.idf"),
    "retail_strip_mall": os.path.join(modeldir, "ASHRAE901_RetailStripmall_STD2019_Denver.idf"),
    "school_primary": os.path.join(modeldir, "ASHRAE901_SchoolPrimary_STD2019_Denver.idf"),
    "school_secondary": os.path.join(modeldir, "ASHRAE901_SchoolSecondary_STD2019_Denver.idf"),
    "warehouse": os.path.join(modeldir, "ASHRAE901_Warehouse_STD2019_Denver.idf"),
}

weather_files = {
    "usa_az_phoenix": os.path.join(weatherdir, "USA_AZ_Phoenix-Sky.Harbor.Intl.AP.722780_TMY3.epw"),
    "usa_ca_fresno": os.path.join(weatherdir, "USA_CA_Fresno.Air.Terminal.723890_TMY3.epw"),
    "usa_ca_san_francisco": os.path.join(weatherdir, "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"),
    "usa_co_boulder": os.path.join(weatherdir, "USA_CO_Boulder-Broomfield-Jefferson.County.AP.724699_TMY3.epw"),
    "usa_co_colorado_springs": os.path.join(weatherdir, "USA_CO_Colorado.Springs-Peterson.Field.724660_TMY3.epw"),
    "usa_co_denver": os.path.join(weatherdir, "USA_CO_Denver-Aurora-Buckley.AFB.724695_TMY3.epw"),
    "usa_co_golden": os.path.join(weatherdir, "USA_CO_Golden-NREL.724666_TMY3.epw"),
    "usa_fl_miami": os.path.join(weatherdir, "USA_FL_Miami.Intl.AP.722020_TMY3.epw"),
    "usa_fl_orlando": os.path.join(weatherdir, "USA_FL_Orlando.Intl.AP.722050_TMY3.epw"),
    "usa_fl_tampa": os.path.join(weatherdir, "USA_FL_Tampa.Intl.AP.722110_TMY3.epw"),
    "usa_il_chicago": os.path.join(weatherdir, "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"),
    "usa_il_uiw": os.path.join(weatherdir, "USA_IL_University.of.Illinois-Willard.AP.725315_TMY3.epw"),
    "usa_nj_newark": os.path.join(weatherdir, "USA_NJ_Newark.Intl.AP.725020_TMY3.epw"),
    "usa_nv_las_vegas": os.path.join(weatherdir, "USA_NV_Las.Vegas-McCarran.Intl.AP.723860_TMY3.epw"),
    "usa_ok_oklahoma": os.path.join(weatherdir, "USA_OK_Oklahoma.City-Will.Rogers.World.AP.723530_TMY3.epw"),
    "usa_va_sterling": os.path.join(weatherdir, "USA_VA_Sterling-Washington.Dulles.Intl.AP.724030_TMY3.epw"),
}
