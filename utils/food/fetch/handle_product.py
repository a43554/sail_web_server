from typing import Optional, List, Tuple

import requests
from bs4 import BeautifulSoup


# Handle product information.
from utils.none import default_if_none


class ProductHandler:

    # Parse the price data.
    @staticmethod
    def parse_prices(product) -> dict:
        # Obtain the primary price.
        primary_price_node = product.find('span', {'class': 'sales ct-tile--price-primary'})
        # Obtain the true price.
        primary_price = float(
            primary_price_node
            .find('span', {'class': 'ct-price-formatted'})
            .text.strip().replace('€', '').replace(',', '.')
        )
        # Obtain the units.
        primary_price_units = (
            primary_price_node
            .find('span', {'class': 'ct-m-unit'})
            .text.strip().replace('/', '')
        )
        # Obtain the discount, if it exists.
        discount = default_if_none(
            data=product.find('p', {'class': 'ct-discount-amount'}),
            if_none=0.0,
            if_not_none=(
                lambda p: (int(p.text.split(':')[-1].strip().replace('%', '')) / 100.0) if "Desconto" in p.text else 0.0
            )
        )
        # Check if discount exists.
        if discount > 0:
            # Obtain the previous price.
            previous_price_node = product.find('span', {'class': 'strike-through list ct-tile--price-dashed'})
            # Obtain the true price.
            previous_price = float(
                previous_price_node
                .find('span', {'class': 'sr-only'}).next_sibling
                .text.strip().replace('€', '').replace(',', '.')
            )
            # Obtain the units.
            previous_price_units = (
                previous_price_node
                .find('span', {'class': 'ct-tile--price-dashed'})
                .text.strip().replace('/', '')
            )
            # The previous uni price.
            previous_unit_price = {
                'amount': previous_price,
                'units': previous_price_units
            }
        # Otherwise, use none.
        else:
            # No previous price.
            previous_unit_price = None

        # Obtain the secondary price.
        secondary_price_node = product.find('div', {'class': 'ct-tile--price-secondary'})
        # Obtain the true price.
        secondary_price = float(
            secondary_price_node
            .find('span', {'class': 'ct-price-value'})
            .text.strip().replace('€', '').replace(',', '.')
        )
        # Obtain the units.
        secondary_price_units = (
            secondary_price_node
            .find('span', {'class': 'ct-m-unit'})
            .text.strip().replace('/', '')
        )
        # Return the price data.
        return {
            'current_unit_price': {
                'amount': primary_price,
                'units': primary_price_units
            },
            'current_price': {
                'amount': secondary_price,
                'units': secondary_price_units
            },
            'discount': discount,
            'previous_unit_price': previous_unit_price
        }

    # Parse amount data.
    @staticmethod
    def analyze_amount(ingredient: dict, product: dict, unit_amount: float) -> Optional[float]:
        # Obtain the product units.
        product_units = product['original_unit_data']['units']
        # Check if it is kilograms.
        if product_units == 'kg':
            # Transform into grams.
            return unit_amount * 1000
        # Check if it's in grams.
        elif product_units == 'gr' or product_units == 'g':
            # Store as grams.
            return unit_amount
        # Check if it's 'ml'.
        elif product_units == 'ml':
            # Compare to the source amount.
            if 'ml' in ingredient['units']:
                # Transform into grams and return.
                return unit_amount * (ingredient['units']['g'] / ingredient['units']['ml'])
            # Compare to the source amount.
            elif 'cl' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount / 10.0) * (ingredient['units']['g'] / (ingredient['units']['cl']))
            # Compare to the source amount.
            elif 'dl' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount / 100.0) * (ingredient['units']['g'] / ingredient['units']['dl'])
            # Compare to the source amount.
            elif 'l' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 1000.0) * (ingredient['units']['g'] / ingredient['units']['l'])
            # Otherwise, do nothing.
            else:
                # Return none.
                return None
        # Check if it's 'cl'.
        elif product_units == 'cl':
            # Compare to the source amount.
            if 'ml' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 10.0) * (ingredient['units']['g'] / ingredient['units']['ml'])
            # Compare to the source amount.
            elif 'cl' in ingredient['units']:
                # Transform into grams and return.
                return unit_amount * (ingredient['units']['g'] / (ingredient['units']['cl']))
            # Compare to the source amount.
            elif 'dl' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount / 10.0) * (ingredient['units']['g'] / ingredient['units']['dl'])
            # Compare to the source amount.
            elif 'l' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount / 100.0) * (ingredient['units']['g'] / ingredient['units']['l'])
            # Otherwise, do nothing.
            else:
                # Return none.
                return None
        # Check if it's 'dl'.
        elif product_units == 'dl':
            # Compare to the source amount.
            if 'ml' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 100.0) * (ingredient['units']['g'] / ingredient['units']['ml'])
            # Compare to the source amount.
            elif 'cl' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 10.0) * (ingredient['units']['g'] / (ingredient['units']['cl']))
            # Compare to the source amount.
            elif 'dl' in ingredient['units']:
                # Transform into grams and return.
                return unit_amount * (ingredient['units']['g'] / ingredient['units']['dl'])
            # Compare to the source amount.
            elif 'l' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount / 10.0) * (ingredient['units']['g'] / ingredient['units']['l'])
            # Otherwise, do nothing.
            else:
                # Return none.
                return None
        # Check if it's 'l'.
        elif product_units == 'l' or product_units == 'lt':
            # Compare to the source amount.
            if 'ml' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 1000.0) * (ingredient['units']['g'] / ingredient['units']['ml'])
            # Compare to the source amount.
            elif 'cl' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 100.0) * (ingredient['units']['g'] / (ingredient['units']['cl']))
            # Compare to the source amount.
            elif 'dl' in ingredient['units']:
                # Transform into grams and return.
                return (unit_amount * 10.0) * (ingredient['units']['g'] / ingredient['units']['dl'])
            # Compare to the source amount.
            elif 'l' in ingredient['units']:
                # Transform into grams and return.
                return unit_amount * (ingredient['units']['g'] / ingredient['units']['l'])
            # Otherwise, do nothing.
            else:
                # Return none.
                return None
        # Otherwise, if no matches do nothing.
        else:
            # If no matches, return null.
            return None

    # Parse the products.
    @staticmethod
    def parse_products(ingredient: dict) -> Tuple[bool, bool, List[dict]]:
        # Make the search term url safe.
        url_safe_name = ingredient['product_name_pt'].replace(' ', '+')
        # The url to search.
        url_to_search = f"https://www.continente.pt/pesquisa/?q={url_safe_name}"
        print(f"\t- Requesting: {url_to_search}")  # LOG
        # Obtain the ingredient page.
        response = requests.get(url_to_search)
        # Use beautifulsoup for parsing.
        html_content = BeautifulSoup(response.content, features="lxml")
        # Obtain the string if no data was found.
        no_search_error = (len(html_content.find_all('span', {'class': 'search-noresults-title'})) == 0)
        # Obtain all squares of information.
        possible_products = html_content.find_all('div', {'class': 'col-12 col-sm-3 col-lg-2 productTile'})
        # The list of products.
        product_list = []
        # Check if a valid product was found.
        has_valid_product = False
        # Iterate through each product:
        for product in possible_products:
            # THe countable text.
            price_primary_text = product.find_next('span', {'class': 'sales ct-tile--price-primary'}).text
            # If the product is countable.
            is_countable = ('/un' in price_primary_text)
            # Deal with countable products.
            if is_countable:
                # Obtain the product amount.
                product_amount_data = (product
                                       .find_next('p', {'class': 'ct-tile--quantity'})
                                       .text
                                       .replace('emb.', '')
                                       .replace('Quant. Mínima = ', '')
                                       .replace('garrafa', '')
                                       .strip().split(' ')
                )
                # Obtain the possible units of the amount.
                unit_amount, unit_amount_units = (
                    float(product_amount_data[0].replace(',', '.')) if len(product_amount_data[0]) > 0 else None,
                    product_amount_data[-1] if len(product_amount_data) > 1 else None
                )
            # Deal with non-countable products.
            else:
                product_amount_data = (
                    product
                        .find_next('p', {'class': 'ct-tile--quantity'})
                        .text.replace('emb.', '').strip().split('=')[-1].strip().split(" ")[0:2]
                )
                # Obtain the possible units of the amount.
                unit_amount, unit_amount_units = (
                    float(product_amount_data[0].replace(',', '.')) if len(product_amount_data[0]) > 0 else None,
                    product_amount_data[-1] if len(product_amount_data) > 1 else None
                )
            # Obtain the product data.
            product = {
                'name': product.find_next('a', {'class': 'ct-tile--description'}).text,
                'brand': product.find_next('p', {'class': 'ct-tile--brand'}).text,
                'valid': False,
                'countable': is_countable,
                'original_unit_data': {
                    'amount': float(product_amount_data[0].replace(',', '.')) if len(product_amount_data[0]) > 0 else None,
                    'units': product_amount_data[-1] if len(product_amount_data) > 1 else None,
                },
                'price': ProductHandler.parse_prices(product)
            }
            # Check if product unit amount is valid.
            if unit_amount is not None:
                # Parse the units.
                amount_in_grams = ProductHandler.analyze_amount(ingredient, product, unit_amount)
            # Otherwise, default to none.
            else:
                # Set the amount as none.
                amount_in_grams = None
            # Check for validity.
            product['valid'] = (amount_in_grams is not None)
            # Transform into grams.
            product['product_unit_data'] = {'amount': amount_in_grams, 'units': 'g'}
            # Check if valid product was found.
            has_valid_product |= product['valid']
            # Append to the list of products.
            product_list.append(product)
            print(f"\t\t- - Product: {product['name']}")  # LOG
            print(f"\t\t- - Original Amount: {product['original_unit_data']['amount']}", end=' ')  # LOG
            print(f"({product['original_unit_data']['units']})")  # LOG
            print(f"\t\t- - Countable: {product['countable']}")  # LOG
            print(f"\t\t- - Converted Amount: {product['product_unit_data']['amount'] if 'product_unit_data' in product else '???'} (g)")  # LOG
            print(f"\t\t- - Price: {product['price']['current_unit_price']['amount']}", end=' ')  # LOG
            print(f"({product['price']['current_unit_price']['units']})")  # LOG
            print(f"\t\t- - Valid: {product['valid']}")  # LOG
            # TODO REMOVE THIS LINE - Break out of the loop after the first product.
            break
        # Return the product list.
        return has_valid_product, no_search_error, product_list
