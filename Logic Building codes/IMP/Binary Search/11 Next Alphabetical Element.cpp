/* Given an array of letters sorted in ascending order,
 find the smallest letter in the the array which is greater than a given key letter.
input : a b c d e
        b
output : c

*/
#include <bits/stdc++.h>
using namespace std;
/*
int main () {
    int n ;
    cin >> n;
    char arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }
    char x;
    cin>> x;
    // ceil = smallest  element just greater than x.
    int start = 0 ;
    int end = n-1;
    char res;

    while ( start <= end) {

        int mid = start + (end-start) /2 ;

        if ( arr[mid] == x) {
           start = mid +1;
           //res = arr[start % n];
           cout<<res<<"1 ";//because we know start can't be greater or equal to size of array.
           //Index 0 to size-1 that is why whenever our start reaches size make sure we start from beginning
        }
        if ( arr[mid] < x) {
            start = mid + 1;
            //res = arr[start % n];
            cout<<res<<"2 "; // IMP
        }
        else if (arr[mid] > x) {
            res = arr[mid];
            cout<<res<<"3 "; // // this is IMP, the greater ele than x can be the possible ans.
            //we want ceil of that element means the element can
            // be greater or equal to that element.
            end = mid -1 ;
        }
    }

    cout << res ;

}
*/

#include <bits/stdc++.h>
using namespace std;

char solve(char arr[], char k, int n)
{
    char ans;
    int start = 0;
    int end = n-1;
    while (start <= end)
    {
        int mid = start + (end - start) / 2;

        if (arr[mid] == k)
        {
            start = mid+1;
        }
        else if (arr[mid] < k)
        {
            start = mid + 1;
        }
        else if (arr[mid] > k)
        {
            ans = arr[mid];
            end = mid - 1;
        }
    }
    return ans;
}

int main()
{
    int n;
    cin >> n;
    char arr[n];
    for (int i = 0; i < n; i++)
    {
        cin>>arr[i];
    }
    char k;
    cin >> k;
    cout << solve(arr, k, n);
}