#include <stdio.h>
#include <cs50.h>
#include <math.h>

int main(void)
{
    // prompts a user for a number, can take longer numbers
    long credit = get_long("Number: ");
    // 4 int variables in order to accommodate different credit card types, two for VISA
    int master = credit / powl(10, 14);
    int amex = credit / powl(10, 13);
    int visa16 = credit / powl(10, 15);
    int visa13 = credit / powl(10, 12);
    // three variables - "second" for every second to last number, "last" for every last number, and "main" which is explained later
    int second = 0;
    int main = 0;
    int last = 0;
    // while loop runs as long as credit is bigger than 0
    while (credit > 0)
    {
        // following algorithm gets the second to last number from credit and multiplies it by 2 as per Luhn's algorithm
        second = ((credit / 10) % 10) * 2;
        // second is two-digit number, go ahead and mod its last number and add 1
        if (second >= 10)
        {
            second = (second % 10) + 1;
        }
        // keeps track of and adds together all second to last numbers of credit
        main = main + second;
        last = last + (credit % 10);
        // credit divided by 100 in order to get to the first number
        credit = credit / 100;
    }
    int sum = main + last;
    // if remainder of sum equals zero continue, otherwise return invalid and exit program
    if (sum % 10 == 0)
    {
        // 3 if clauses to accommodate all three credit card types - to achieve validity of provided card number, its corresponding length and first digit(s) are checked
        if (master == 51 || master == 52 || master == 53 || master == 54 || master == 55)
        {
            printf("MASTERCARD\n");
            return 0;
        }
        else if (amex == 34 || amex == 37)
        {
            printf("AMEX\n");
            return 0;
        }
        else if (visa16 == 4 || visa13 == 4)
        {
            printf("VISA\n");
            return 0;
        }
        else
        {
            printf("INVALID\n");
            return 0;
        }
    }
    else
    {
        printf("INVALID\n");
        return 0;
    }
}