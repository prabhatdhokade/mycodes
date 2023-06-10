/*Given a string you need to print all possible strings that can be made by 
placing spaces (zero or one) in between them. Output should be printed in sorted 
increasing order of strings.

Input:  str[] = "ABC"
Output: (A B C)(A BC)(AB C)(ABC)


plz chek out the video again this imp question   
*/
#include<bits/stdc++.h>

using namespace std;
void solve(string ip,string op) {
    if(ip.size() == 0) {
        cout<<op<<", ";
        return;
    }
    string op1 = op;
    string op2 = op;
    op1.push_back('_');   // for puttinng space, whole point of programm was in this two steps
    op1.push_back(ip[0]); // for including character wiht space // and this one
    op2.push_back(ip[0]);// pass without including space
    ip.erase(ip.begin() + 0); //delte element after passing 
    solve(ip,op1);
    solve(ip,op2);
    return;

}
int main() 
{
    string s1;
    cin >> s1;
    string s2; // for output purpose
    s2.push_back(s1[0]); //give the first index of the input string
    s1.erase(s1.begin() + 0);
    solve(s1,s2);
}

