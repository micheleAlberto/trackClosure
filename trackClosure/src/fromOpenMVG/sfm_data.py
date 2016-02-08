import json

def read():
    with open('data/sfm_data.json') as f:
        return json.load(f)
    
a=read()
a['intrinsics']


def make_pinhole_radial_k3
{
            "key": 0,
            "value": {
                "polymorphic_id": 2147483649,
                "polymorphic_name": "pinhole_radial_k3",
                "ptr_wrapper": {
                    "id": 2147483721,
                    "data": {
                        "width": 2560,
                        "height": 1920,
                        "focal_length": 14068.739101872479,
                        "principal_point": [
                            1364.8152628839086,
                            813.58976326886238
                        ],
                        "disto_k3": [
                            25.115168983820872,
                            -6510.9493073519543,
                            444573.51040456677
                        ]
                    }
                }
            }
        }
